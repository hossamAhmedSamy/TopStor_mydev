#!/usr/bin/sh

# Function to handle updating a specific directory with git
fnupdate () {
	echo '###########################################' $1
	# Clean up any __pycache__ directories
	rm -rf __pycache__ *.pyc
	git add --all
	git commit -am'Applying updates from zip'
	git branch -D $1
	git checkout -b $1
	git pull origin $1
	if [ $? -ne 0 ]; then
		echo "Something went wrong while updating $1 "
		exit 1
	fi
	sync
	sync
	sync
}

# Define jobs for directories
cjobs=("TopStor" "pace" "topstorweb")

# Get the branch name from arguments
branch=$1
branchc=$(echo $branch | wc -c)

if [ $branchc -le 3 ]; then
	echo "No valid branch is supplied .... exiting"
	exit 1
fi 

# Check if we should use the same branch
echo $branch | grep samebranch
if [ $? -eq 0 ]; then
	branch=$(git branch | grep '*' | awk '{print $2}')
fi

# Unzip the file
zipfile="/TopStordata/$2"
if [ ! -f $zipfile ]; then
	echo "Zip file $zipfile not found!"
	exit 1
fi

echo "Unzipping $zipfile..."
unzip -o -P "$2" $zipfile -d /TopStordata/unzipped

if [ $? -ne 0 ]; then
	echo "Failed to unzip the file."
	exit 1
fi

# Loop through jobs and update the corresponding directories
flag=1
while [ $flag -ne 0 ]; do
	rjobs=("${cjobs[@]}")
	echo "Remaining jobs: ${rjobs[@]}"
	for job in "${rjobs[@]}"; do
		echo "Processing $job..."
		cd /$job
		if [ $? -ne 0 ]; then
			echo "The directory $job is not found... exiting"
			exit 1
		fi

		# Copy unzipped content to the respective directory
		if [ -d "/TopStordata/unzipped/$job" ]; then
			cp -r /TopStordata/unzipped/$job/* /$job/
			echo "Merged content from /TopStordata/unzipped/$job into /$job"
		else
			echo "No content for $job found in the unzipped folder"
		fi
		
		# Update the directory using git
		fnupdate $branch 

		# Remove job from the list
		cjobs=("${cjobs[@]/$job/}")
	done

	# Check if all jobs are done
	lencjobs=$(echo ${#cjobs[@]})
	if [ $lencjobs -le 0 ]; then
		flag=0
	fi
done

# Final check and confirmation
cd /TopStor
git show | grep commit
echo "Update process finished!"
