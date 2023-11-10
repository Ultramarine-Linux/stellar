# Postinstall hook for Anaconda
# put this file in /usr/share/anaconda/post-scripts

%post --nochroot
export STELLAR_CHROOT=/mnt/sysroot

# only run Install driver code for now
python -m umstellar.driver


%end

# no seriously, that's it
