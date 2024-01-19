from google.cloud.aiplatform.prediction import LocalModel

project = "gpeg-externalization-platform"
location = "asia-east1"  # Replace with your preferred location

predict_route = "/predictions/model"
health_route = "/ping"
serving_container_ports = [8080]
container_uri = "gcr.io/gpeg-externalization-platform/keybert-model:0.0.1"

# TO run the model with torchserve
# torchserve --no-config-snapshots --model-store archived_model/ --start --models all

print('Local Model loading')
local_model = LocalModel(
    serving_container_image_uri=container_uri,
    serving_container_predict_route=predict_route,
    serving_container_health_route=health_route,
    serving_container_ports=serving_container_ports
    )

print('deploying ..')
with local_model.deploy_to_local_endpoint() as local_endpoint:
    # health_check_response = local_endpoint.run_health_check()
 
    predict_response = local_endpoint.predict(
        request_file="instances.json",
        headers={"Content-Type": "application/json"},
    )

    print(predict_response, predict_response.content)


local_endpoint.print_container_logs(show_all=True)
