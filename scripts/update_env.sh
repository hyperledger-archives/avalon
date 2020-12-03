#!/bin/bash

distro=""
image=""
file=""

while getopts 'f:d:i:h' OPTCHAR ; do
	case $OPTCHAR in
		d )
			distro="DISTRO=$OPTARG"
			;;

		i )
			image="IMAGE=$OPTARG"
			;;

                f)
			file=$OPTARG
			;;
			
		h )
			echo hello
	esac
done

echo $distro
echo $image

a=$(sed -n '/DISTRO=/=' $file)
sed -i "${a}s/.*/${distro}/" $file
a=$(sed -n '/IMAGE=/=' $file)
sed -i "${a}s/.*/${image}/" $file
