import time
from pathlib import Path
from flask import Flask, request, jsonify
from detect import run
import uuid
import yaml
from loguru import logger
import os
import boto3
from pymongo import MongoClient

app = Flask(__name__)

# Load environment variables
images_bucket = os.environ['BUCKET_NAME']
aws_key_id = os.environ['AWS_KEY_ID']
aws_secret_key = os.environ['AWS_ACCESS_KEY']
mongodb_uri = os.environ["MONGO_URI"]

# Start mongo client
client = MongoClient(mongodb_uri)
db = client["docker_proj_db"]
collection = db["docker_proj_collection"]

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

# Start a boto3 client to communicate with the S3 bucket
s3 = boto3.client('s3', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_secret_key)

@app.route('/predict', methods=['POST'])
def predict():
    # Generates a UUID for this current prediction HTTP request. This id can be used as a reference in logs to identify and track individual prediction requests.
    prediction_id = str(uuid.uuid4())
    logger.info(f'prediction: {prediction_id}. start processing')

    # Receives a URL parameter representing the image to download from S3
    img_name = request.args.get('imgName')

    original_img_path = img_name
    if "photos" in img_name:
        os.makedirs("photos", exist_ok=True)
        img_name = img_name.split('/')[-1]  
        
    # TODO download img_name from S3, store the local image path in original_img_path
    #  The bucket name should be provided as an env var BUCKET_NAME.
    try:
        s3.download_file(images_bucket, original_img_path, original_img_path)
        logger.info(f'prediction: {prediction_id}/{original_img_path}. Download img completed')
    except Exception as e:
        logger.error(f'Error downloading image from S3:{e}')
        return 'Error downloading image from S3'
    
    # Predicts the objects in the image
    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=original_img_path,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction: {prediction_id}/{original_img_path}. done')

    # This is the path for the predicted image with labels
    # The predicted image typically includes bounding boxes drawn around the detected objects, along with class labels and possibly confidence scores.
    predicted_img_path = Path(f'static/data/{prediction_id}/{img_name}')
    
    # TODO Uploads the predicted image (predicted_img_path) to S3.
    s3_key = f'predictions/{img_name}'
    try:
        s3.upload_file(str(predicted_img_path), images_bucket, s3_key)
    except Exception as e:
        logger.error(f'Error uploading predicted image to S3:{e}')
        return 'Error uploading predicted image to S3'
    
    # Parse prediction labels and create a summary
    pred_summary_path = Path(f'static/data/{prediction_id}/labels/{img_name.split(".")[0]}.txt')
    if pred_summary_path.exists():
        with open(pred_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': str(original_img_path),
            'predicted_img_path': str(predicted_img_path),
            'labels': labels,
            'time': time.time()
        }

        # TODO: Store the prediction_summary in MongoDB
        collection.insert_one(prediction_summary)

        # Mongo adds this filed and needs to be json serilizable
        prediction_summary["_id"] = str(prediction_summary["_id"])

        return jsonify(prediction_summary)
    else:
        return f'prediction: {prediction_id}/{original_img_path}. prediction result not found', 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)