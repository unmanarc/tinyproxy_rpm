#
# spec file for package tinyproxy
#
# Copyright (c) 2021 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


Name:           tinyproxy
Version:        1.11.0
Release:        2
Summary:        Minimalist WWW proxy
License:        GPL-2.0-or-later
Group:          Productivity/Networking/Web/Proxy
URL:            https://tinyproxy.github.io/
Source:         https://github.com/tinyproxy/tinyproxy/releases/download/%version/tinyproxy-%version.tar.xz
Source1:        %name.logrotate
Patch1:         tinyproxy-conf.patch
BuildRequires:  asciidoc
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libxslt
BuildRequires:  systemd-rpm-macros
BuildRequires:  xz
Requires:       logrotate

%description
Tinyproxy is a light-weight HTTP/HTTPS proxy daemon for POSIX
operating systems. Designed from the ground up to be fast and yet
small, it is an ideal solution for use cases such as embedded
deployments where a full featured HTTP proxy is required, but the
system resources for a larger proxy are unavailable.

%prep
%autosetup -p1

%build
autoreconf -fiv
%configure --bindir="%_prefix/sbin"
%make_build

%install
%make_install
b="%buildroot"
install -d -m0750 "$b/%_localstatedir/log/%name"
install -D -m0644 "%SOURCE1" "$b/%_sysconfdir/logrotate.d/%name"

mkdir -p "$b/%_unitdir" "$b/%_prefix/lib/tmpfiles.d"
cat >>"$b/%_unitdir/tinyproxy.service" <<-EOF
	[Unit]
	Description=A small HTTP/1 proxy
	After=network.target named.service nss-lookup.service
	[Service]
	Type=simple
	ExecStart=%_sbindir/tinyproxy -d
	CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_SETGID CAP_SETUID
	[Install]
	WantedBy=multi-user.target
EOF
cat >>"$b/%_prefix/lib/tmpfiles.d/tinyproxy.conf" <<-EOF
	d /run/tinyproxy 0755 tinyproxy tinyproxy -
EOF
install -d -m 755 "$b/%_sbindir"
ln -sf service "$b/%_sbindir/rc%name"

rm -rf "$b%_datadir/doc/%name"

%pre
getent group tinyproxy >/dev/null || groupadd -r tinyproxy
getent passwd tinyproxy >/dev/null || \
	useradd -c "Tinyproxy" -d "%_datadir/%name" -g tinyproxy \
	-r -s /bin/false tinyproxy
%service_add_pre tinyproxy.service

%post
systemd-tmpfiles --create tinyproxy.conf || :
%service_add_post tinyproxy.service

%preun
%service_del_preun tinyproxy.service

%postun
%service_del_postun tinyproxy.service

%files
%doc NEWS README README.md
%dir %_sysconfdir/%name
%config(noreplace) %_sysconfdir/%name/*.conf
%config %_sysconfdir/logrotate.d/%name
%_sbindir/tinyproxy
%_sbindir/rctinyproxy
%_mandir/man*/*
%_datadir/%name
%_unitdir/*.service
%_prefix/lib/tmpfiles.d/
%attr(750,%name,root) %_localstatedir/log/%name

%changelog
* Sat Jan 22 2022 Aaron G. Mizrachi P. <aaron@unmanarc.com>
- Ported to COPR / RHEL
* Fri Apr 16 2021 Jan Engelhardt <jengelh@inai.de>
- Update to release 1.11
  * Support for multiple bind directives.
* Tue Aug 25 2020 Jan Engelhardt <jengelh@inai.de>
- Do not suppress errors from groupadd/useradd
* Thu Aug 20 2020 Dirk Mueller <dmueller@suse.com>
- update to 1.10.0:
  * Configuration file has moved from /etc/tinyproxy.conf to
    /etc/tinyproxy/tinyproxy.conf.
  * Add support for basic HTTP authentication
  * Add socks upstream support
  * Log to stdout if no logfile is specified
  * Activate reverse proxy by default
  * Support bind with transparent mode
  * Allow multiple listen statements in the configuration
  * Fix CVE-2017-11747: Create PID file before dropping privileges.
  * Fix CVE-2012-3505: algorithmic complexity DoS in hashmap
  * Bugfixes
  * BB#110: fix algorithmic complexity DoS in hashmap
  * BB#106: fix CONNECT requests with IPv6 literal addresses as host
  * BB#116: fix invalid free for GET requests to ipv6 literal address
  * BB#115: Drop supplementary groups
  * BB#109: Fix crash (infinite loop) when writing to log file fails
  * BB#74: Create log and pid files after we drop privs
  * BB#83: Use output of id instead of $USER
* Tue Jan  6 2015 jengelh@inai.de
- Provide service file instead of script
* Mon Dec 29 2014 jengelh@inai.de
- Update to new upstream release 1.8.4
  * Fix crash (infinite loop) when logfile writing fails
  * Allow listening on multiple families when no Listen is
  provided in config.
  * Fix CONNECT requsts with IPv6 literal addresses as host.
  * Fix invalid free when connecting to ipv6 literal address
  * Limit the number of headers per request to prevent DoS
- Remove 110-seeding.diff (merged upstream), 110-headerlimit.diff
  (solved upstream)
* Fri Mar 14 2014 boris@steki.net
- Remove stray chunk headers that can cause /usr/bin/patch to fail
* Thu Jul  4 2013 jengelh@inai.de
- Add 110-seeding.diff, 110-headerlimit.diff to address
  CVE-2012-3505 (bnc#776506)
- Refresh tinyproxy-conf.patch to be in -p1 format rather than -p0
* Wed Feb 22 2012 chris@computersalat.de
- fix init script
  * TINYPROXY_CFG=/etc/tinyproxy.conf
  * create PID DIR
- fix logrotate script
  * compress, dateext .....
- add user, group tinyproxy
- add conf patch
- add missing logdir
- add missing rc_link
- fix pre/post
* Fri Dec  2 2011 chris@computersalat.de
- spec-cleaner
- fix build for suse_version 1110
  * define missing _initdir macro
* Mon Sep 19 2011 toganm@opensuse.org
- Update to 1.8.3 version
  changed source format to bz2
  * Fix upstream proxy support
  * Fix FilterURLs with transparent proxy support
  * Fix bug in ACL netmask generation
* Fri Jul 29 2011 toganm@opensuse.org
- added /etc/init.d/tinyproxy
- added tinyproxy logrotate
* Mon Jul 18 2011 jengelh@medozas.de
- Initial package
