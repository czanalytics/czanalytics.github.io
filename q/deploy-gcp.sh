# deploy-gcp.sh
# Deploy api to GCP
# https://medium.com/@taylorhughes/how-to-deploy-an-existing-docker-container-project-to-google-cloud-run-with-the-minimum-amount-of-daca0b5978d8
# Use: source deploy-gcp.sh

export REGION="europe-north1-a"
export GCLOUD_PROJECT="calculator" #  
export REPO="price"
export IMAGE="api"

export TAG=${REGION}-docker.pkg.dev/$GCLOUD_PROJECT/$REPO/$IMAGE

docker build -t $TAG -f Dockerfile --platform linux/x86_64 .

# push image to Artifact Registry:
#docker push $IMAGE_TAG 
