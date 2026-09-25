import os
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_score,
    recall_score,
    f1_score
)

from sklearn.utils.class_weight import compute_class_weight


# ============================================================
# 1. CONFIGURATION
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

DATASET_DIR = "C:/Users/Admin/Downloads/archive (1)"

JAUNDICE_DIR = os.path.join(DATASET_DIR, "Jaundice")
NORMAL_DIR = os.path.join(DATASET_DIR, "Normal")

MODEL_DIR = "models"
OUTPUT_DIR = "outputs"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16

INITIAL_EPOCHS = 15
FINE_TUNE_EPOCHS = 20

# Probability threshold used only for this prototype.
# Do NOT interpret this as a clinically validated threshold.
THRESHOLD = 0.50


# ============================================================
# 2. CHECK DATASET
# ============================================================

if not os.path.exists(JAUNDICE_DIR):
    raise FileNotFoundError(
        f"Jaundice folder not found: {JAUNDICE_DIR}"
    )

if not os.path.exists(NORMAL_DIR):
    raise FileNotFoundError(
        f"Normal folder not found: {NORMAL_DIR}"
    )


# ============================================================
# 3. COLLECT IMAGE PATHS
# ============================================================

VALID_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)


def collect_images(folder, label):

    records = []

    for filename in os.listdir(folder):

        if filename.lower().endswith(VALID_EXTENSIONS):

            path = os.path.join(folder, filename)

            records.append({
                "filepath": path,
                "label": label
            })

    return records


# Label:
# 0 = Normal
# 1 = Jaundice

normal_images = collect_images(
    NORMAL_DIR,
    0
)

jaundice_images = collect_images(
    JAUNDICE_DIR,
    1
)

records = normal_images + jaundice_images

df = pd.DataFrame(records)

print("\n======================================")
print("DATASET INFORMATION")
print("======================================")

print(f"Total images    : {len(df)}")
print(f"Normal images   : {(df['label'] == 0).sum()}")
print(f"Jaundice images: {(df['label'] == 1).sum()}")

print("\nClass distribution:")
print(df["label"].value_counts())


# ============================================================
# 4. REMOVE DUPLICATE FILE PATHS
# ============================================================

df = df.drop_duplicates(subset=["filepath"])

print("\nAfter removing duplicate paths:")
print(len(df))


# ============================================================
# 5. TRAIN / VALIDATION / TEST SPLIT
# ============================================================

# 70% training
# 15% validation
# 15% testing

train_df, temp_df = train_test_split(
    df,
    test_size=0.30,
    stratify=df["label"],
    random_state=SEED
)

val_df, test_df = train_test_split(
    temp_df,
    test_size=0.50,
    stratify=temp_df["label"],
    random_state=SEED
)


print("\n======================================")
print("DATA SPLIT")
print("======================================")

print(f"Training   : {len(train_df)}")
print(f"Validation : {len(val_df)}")
print(f"Testing    : {len(test_df)}")

print("\nTraining distribution:")
print(train_df["label"].value_counts())

print("\nValidation distribution:")
print(val_df["label"].value_counts())

print("\nTesting distribution:")
print(test_df["label"].value_counts())


# Save split information
train_df.to_csv(
    os.path.join(OUTPUT_DIR, "train_split.csv"),
    index=False
)

val_df.to_csv(
    os.path.join(OUTPUT_DIR, "validation_split.csv"),
    index=False
)

test_df.to_csv(
    os.path.join(OUTPUT_DIR, "test_split.csv"),
    index=False
)


# ============================================================
# 6. TF.DATA PIPELINE
# ============================================================

def load_image(path, label):

    image = tf.io.read_file(path)

    image = tf.image.decode_image(
        image,
        channels=3,
        expand_animations=False
    )

    image = tf.image.resize(
        image,
        IMAGE_SIZE
    )

    image = tf.cast(
        image,
        tf.float32
    )

    # Keep pixels in 0-255 here.
    # EfficientNet preprocessing is handled by Keras.
    return image, tf.cast(label, tf.float32)


def create_dataset(dataframe, shuffle=False):

    paths = dataframe["filepath"].values
    labels = dataframe["label"].values

    dataset = tf.data.Dataset.from_tensor_slices(
        (paths, labels)
    )

    dataset = dataset.map(
        load_image,
        num_parallel_calls=tf.data.AUTOTUNE
    )

    if shuffle:
        dataset = dataset.shuffle(
            buffer_size=len(dataframe),
            seed=SEED
        )

    dataset = dataset.batch(
        BATCH_SIZE
    )

    dataset = dataset.prefetch(
        tf.data.AUTOTUNE
    )

    return dataset


train_ds = create_dataset(
    train_df,
    shuffle=True
)

val_ds = create_dataset(
    val_df
)

test_ds = create_dataset(
    test_df
)


# ============================================================
# 7. DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential(
    [
        tf.keras.layers.RandomFlip(
            "horizontal"
        ),

        tf.keras.layers.RandomRotation(
            0.05
        ),

        tf.keras.layers.RandomZoom(
            0.10
        ),

        tf.keras.layers.RandomTranslation(
            height_factor=0.05,
            width_factor=0.05
        ),

        tf.keras.layers.RandomContrast(
            0.10
        ),
    ],
    name="data_augmentation"
)


# ============================================================
# 8. BUILD MODEL
# ============================================================

print("\n======================================")
print("BUILDING EFFICIENTNET-B0")
print("======================================")


base_model = tf.keras.applications.EfficientNetB0(
    include_top=False,
    weights="imagenet",
    input_shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    )
)


# Initially freeze pretrained network
base_model.trainable = False


inputs = tf.keras.Input(
    shape=(
        IMAGE_SIZE[0],
        IMAGE_SIZE[1],
        3
    ),
    name="image"
)


x = data_augmentation(inputs)

x = base_model(
    x,
    training=False
)

x = tf.keras.layers.GlobalAveragePooling2D()(x)

x = tf.keras.layers.Dense(
    256,
    activation="relu"
)(x)

x = tf.keras.layers.Dropout(
    0.40
)(x)

outputs = tf.keras.layers.Dense(
    1,
    activation="sigmoid",
    name="jaundice_probability"
)(x)


model = tf.keras.Model(
    inputs,
    outputs
)


# ============================================================
# 9. COMPILE MODEL
# ============================================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-3
    ),

    loss=tf.keras.losses.BinaryCrossentropy(),

    metrics=[
        tf.keras.metrics.BinaryAccuracy(
            name="accuracy"
        ),

        tf.keras.metrics.Precision(
            name="precision"
        ),

        tf.keras.metrics.Recall(
            name="recall"
        ),

        tf.keras.metrics.AUC(
            name="auc"
        )
    ]
)


model.summary()


# ============================================================
# 10. CLASS WEIGHTS
# ============================================================

classes = np.array([0, 1])

weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=train_df["label"].values
)

class_weights = {
    int(classes[i]): float(weights[i])
    for i in range(len(classes))
}

print("\nClass weights:")
print(class_weights)


# ============================================================
# 11. CALLBACKS
# ============================================================

best_model_path = os.path.join(
    MODEL_DIR,
    "best_jaundice_model.keras"
)

callbacks = [

    tf.keras.callbacks.ModelCheckpoint(
        best_model_path,
        monitor="val_auc",
        mode="max",
        save_best_only=True,
        verbose=1
    ),

    tf.keras.callbacks.EarlyStopping(
        monitor="val_auc",
        mode="max",
        patience=5,
        restore_best_weights=True,
        verbose=1
    ),

    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.3,
        patience=2,
        min_lr=1e-7,
        verbose=1
    )
]


# ============================================================
# 12. INITIAL TRAINING
# ============================================================

print("\n======================================")
print("PHASE 1: TRANSFER LEARNING")
print("======================================")


history1 = model.fit(
    train_ds,

    validation_data=val_ds,

    epochs=INITIAL_EPOCHS,

    class_weight=class_weights,

    callbacks=callbacks
)


# ============================================================
# 13. FINE-TUNING
# ============================================================

print("\n======================================")
print("PHASE 2: FINE-TUNING")
print("======================================")


base_model.trainable = True


# Freeze early layers.
# Train only the later portion of EfficientNet.
fine_tune_from = 180

for layer in base_model.layers[:fine_tune_from]:

    layer.trainable = False


model.compile(
    optimizer=tf.keras.optimizers.Adam(
        learning_rate=1e-5
    ),

    loss=tf.keras.losses.BinaryCrossentropy(),

    metrics=[
        tf.keras.metrics.BinaryAccuracy(
            name="accuracy"
        ),

        tf.keras.metrics.Precision(
            name="precision"
        ),

        tf.keras.metrics.Recall(
            name="recall"
        ),

        tf.keras.metrics.AUC(
            name="auc"
        )
    ]
)


history2 = model.fit(
    train_ds,

    validation_data=val_ds,

    epochs=FINE_TUNE_EPOCHS,

    class_weight=class_weights,

    callbacks=callbacks
)


# ============================================================
# 14. LOAD BEST MODEL
# ============================================================

print("\nLoading best model...")

model = tf.keras.models.load_model(
    best_model_path
)


# ============================================================
# 15. TEST EVALUATION
# ============================================================

print("\n======================================")
print("TEST SET EVALUATION")
print("======================================")


test_results = model.evaluate(
    test_ds,
    verbose=1
)

for name, value in zip(
    model.metrics_names,
    test_results
):
    print(
        f"{name}: {value:.4f}"
    )


# ============================================================
# 16. GET TEST PREDICTIONS
# ============================================================

y_true = test_df["label"].values

y_probability = model.predict(
    test_ds,
    verbose=1
).ravel()


y_pred = (
    y_probability >= THRESHOLD
).astype(int)


# ============================================================
# 17. CLASSIFICATION REPORT
# ============================================================

print("\n======================================")
print("CLASSIFICATION REPORT")
print("======================================")


print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "Normal",
            "Jaundice"
        ],
        digits=4
    )
)


# ============================================================
# 18. METRICS
# ============================================================

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0
)

auc = roc_auc_score(
    y_true,
    y_probability
)


print("\n======================================")
print("IMPORTANT METRICS")
print("======================================")

print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-score  : {f1:.4f}")
print(f"ROC-AUC   : {auc:.4f}")


# ============================================================
# 19. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_true,
    y_pred
)


print("\nConfusion Matrix:")
print(cm)


plt.figure(
    figsize=(6, 5)
)

plt.imshow(
    cm,
    interpolation="nearest"
)

plt.title(
    "Jaundice Screening - Confusion Matrix"
)

plt.colorbar()

plt.xticks(
    [0, 1],
    ["Normal", "Jaundice"]
)

plt.yticks(
    [0, 1],
    ["Normal", "Jaundice"]
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
)

for i in range(2):

    for j in range(2):

        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )


plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "confusion_matrix.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# 20. ROC CURVE
# ============================================================

fpr, tpr, thresholds = roc_curve(
    y_true,
    y_probability
)


plt.figure(
    figsize=(7, 6)
)

plt.plot(
    fpr,
    tpr,
    label=f"ROC-AUC = {auc:.4f}"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--"
)

plt.xlabel(
    "False Positive Rate"
)

plt.ylabel(
    "True Positive Rate"
)

plt.title(
    "Jaundice Screening ROC Curve"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "roc_curve.png"
    ),
    dpi=300
)

plt.close()


# ============================================================
# 21. SAVE TEST PREDICTIONS
# ============================================================

results_df = test_df.copy()

results_df["probability"] = y_probability

results_df["prediction"] = y_pred

results_df["prediction_name"] = results_df[
    "prediction"
].map(
    {
        0: "Normal",
        1: "Jaundice"
    }
)

results_df.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "test_predictions.csv"
    ),
    index=False
)


# ============================================================
# 22. SAVE FINAL MODEL
# ============================================================

final_model_path = os.path.join(
    MODEL_DIR,
    "jaundice_screening_model.keras"
)

model.save(
    final_model_path
)


print("\n======================================")
print("TRAINING COMPLETE")
print("======================================")

print(
    f"Model saved to:\n{final_model_path}"
)

print(
    f"\nConfusion matrix:\n"
    f"{OUTPUT_DIR}/confusion_matrix.png"
)

print(
    f"\nROC curve:\n"
    f"{OUTPUT_DIR}/roc_curve.png"
)

print(
    f"\nTest predictions:\n"
    f"{OUTPUT_DIR}/test_predictions.csv"
)