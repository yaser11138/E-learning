import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import cloudinary
import cloudinary.uploader
import cloudinary.api


def upload_file_to_cloudinary(file, folder="e-learning"):
    """
    Upload a file to Cloudinary and return the URL.

    Args:
        file: The file to upload
        folder: The folder in Cloudinary to store the file

    Returns:
        dict: Contains the URL and other metadata of the uploaded file
    """
    try:
        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto",  # Automatically detect if it's an image or video
            eager=[
                {"format": "mp4", "quality": "auto"},  # For videos
                {"format": "webp", "quality": "auto"},  # For images
            ],
            eager_async=True,
        )

        return {
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "format": result["format"],
            "resource_type": result["resource_type"],
        }
    except Exception as e:
        # Log the error and return None
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None


def delete_file_from_cloudinary(public_id):
    """
    Delete a file from Cloudinary.

    Args:
        public_id: The public_id of the file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"Error deleting from Cloudinary: {str(e)}")
        return False


def get_file_url(public_id):
    """
    Get the URL of a file from Cloudinary.

    Args:
        public_id: The public_id of the file

    Returns:
        str: The URL of the file
    """
    try:
        return cloudinary.CloudinaryImage(public_id).build_url()
    except Exception as e:
        print(f"Error getting file URL: {str(e)}")
        return None


def validate_file(file, max_size_mb=100, allowed_types=None):
    """
    Validate a file before uploading.

    Args:
        file: The file to validate
        max_size_mb: Maximum file size in MB
        allowed_types: List of allowed file types

    Returns:
        tuple: (is_valid, error_message)
    """
    if allowed_types is None:
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "video/mp4",
            "video/webm",
        ]

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False, f"File size must be less than {max_size_mb}MB"

    # Check file type
    if file.content_type not in allowed_types:
        return (
            False,
            f"File type not allowed. Allowed types: {', '.join(allowed_types)}",
        )

    return True, None
