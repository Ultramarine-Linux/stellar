# Postinstall hook for Anaconda
# put this file in /usr/share/anaconda/post-scripts

%post --nochroot
export STELLAR_CHROOT=/mnt/sysroot
python -m umstellar


%end

# no seriously, that's it
