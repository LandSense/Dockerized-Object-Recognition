
In order to use the application the user will need docker installed on their local machine. Follow these steps to create the appropriate docker components and access the service.

1. Run docker build on the Dockerfile at /vanillatf/Dockerfile, ensuring to name the image tensorflow (remember docker build takes a directory containing the context, in this case the Dockerfile):  
```sudo docker build -t tensorflow vanillatf ```
2. Once this is built run docker build on the Dockerfile in the root of the repo:
```sudo docker build -t tensorflowapp .```
3. Following this launch and run a container from the tensorflowapp image:
```sudo docker run --restart always --name tensorflowapp -p 5000:5000 -d -it tensorflowapp```
4. Now access the service on http://0.0.0.0:5000/, browse to the desired image to process, click upload and the image should be returned by the object recognition app.
