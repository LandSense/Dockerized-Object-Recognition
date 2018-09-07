# Detecting faces and number plates

This applicaiton is intended for use in the Landsense project. The primary purpose is to provide an example object recognition application for use with swagger tools.

The application uses:

1. Docker as a host
2. The python flask microframework for the server
3. The Tensorflow python library and the associated object recognition api for the machine learning components

# Steps for use

In order to use the application the user will need docker installed on their local machine. Follow these steps to create the appropriate docker components and access the service.

1. Run docker build on the Dockerfile at /vanillatf/Dockerfile, ensuring to name the image tensorflow: 
   sudo docker build -t tensorflow vanillatf (remember docker build takes a directory containing the context in this case the Dockerfile)
2. Once this is built run docker build on the Dockerfile in the root of the repo
   sudo docker build -t tensorflow .
3. Following this launch and run a container from the tensorflowapp image:
   sudo docker run --restart always --name tensorflowapp -p 5000:5000 -d -it tensorflowapp
4. Now access the service on http://0.0.0.0:5000/, browse to the desired image to process, click upload and the image should be returned by the object recognition app.


# Sending a POST
The response can also be programmatically recieved should the user wish to process the output image further

For example an image can be sent and recieved using curl:
curl --output myimage.jpeg --form "image=@/home/theo/Documents/balls.jpeg" http://0.0.0.0:5000/upload


#Intended improvements:

1. optimize docker files
2. create docker compose file to auto generate primary and dependant images
3. process other file formats
4. swap flask with production WSGI server
