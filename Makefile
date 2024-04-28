# This makefile only installs the stellar-firstboot script and the desktop file
# If you want the Python module, use pip
install:
	# Copy scripts
	install -m 755 stellar-firstboot /usr/libexec
	install stellar-firstboot.desktop /etc/xdg/autostart
	install com.fyralabs.pkexec.umstellar-firstboot.policy /usr/share/polkit-1/actions

