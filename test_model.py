import sys
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError


MODEL_PATH = "models/jaundice_screening_model.keras"
IMG_SIZE = (224, 224)
THRESHOLD = 0.50


def load_image(image_path):
    try:
        image = Image.open(image_path)

        # Convert anything supported by PIL to RGB
        image = image.convert("RGB")

        original_size = image.size

        image = image.resize(IMG_SIZE)

        image_array = np.array(image, dtype=np.float32)

        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)

        return image_array, original_size

    except UnidentifiedImageError:
        raise ValueError("The file is not a valid/recognized image.")

    except Exception as e:
        raise ValueError(f"Could not load image: {e}")


def predict(image_path):

    print("\nLoading model...")
    model = tf.keras.models.load_model(MODEL_PATH)

    print("Loading image...")
    image, original_size = load_image(image_path)

    prediction = model.predict(image, verbose=0)

    jaundice_probability = float(prediction[0][0])

    if jaundice_probability >= THRESHOLD:
        result = "POSSIBLE JAUNDICE"
    else:
        result = "NOT FLAGGED"

    print("\n" + "=" * 50)
    print("JAUNDICE SCREENING RESULT")
    print("=" * 50)

    print(f"Image       : {image_path}")
    print(f"Original size: {original_size[0]} x {original_size[1]}")
    print(f"Jaundice probability: {jaundice_probability:.4f}")
    print(f"Jaundice probability: {jaundice_probability * 100:.2f}%")
    print(f"\nResult: {result}")

    print("\n" + "-" * 50)
    print("IMPORTANT")
    print("-" * 50)
    print(
        "This is an AI screening result from a prototype model. "
        "It is NOT a confirmed medical diagnosis."
    )
    print("=" * 50)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python test_image.py <image_path>")
        print("\nExamples:")
        print("python test_image.py newborn.jpg")
        print("python test_image.py photo.png")
        print("python test_image.py image.webp")
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    try:
        predict(str(image_path))

    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)