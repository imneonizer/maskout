export DISPLAY=:1
xhost +
docker run --rm -it --gpus all \
	-v $(pwd):/opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps/apps/maskout \
	-v /media/LFS/nitin/videos:/videos \
	-e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix --net host \
	--name maskout-ds-container --hostname maskout \
	maskout bash
