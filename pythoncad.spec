%{expand: %%define pyver %(python -c 'import sys;print(sys.version[0:3])')}

# platform defines - set one below or define the build_xxx on the command line
#
# fixme: add a Fedora line in here ...
#
%define rhel 0
%{?build_rhel:%define rhel 1}
%define suse 0
%{?build_suse:%define suse 1}
%define mdk 0
%{?build_mdk:%define mdk 1}

# test for a platform definition
%if ! %{rhel} && ! %{suse} && ! %{mdk}
%{error: You must specify a platform. Please examine the spec file.}
exit 1
%endif

%define _version DS1-R36

Summary: PythonCAD scriptable CAD package
Name: PythonCAD
Version: 0.1.36
Release: 1
Group: Applications/Engineering
License: GPL v2
Source: %{name}-%{_version}.tar.gz
#Patch0: %{_version}.patch
BuildRoot: %{_tmppath}/%{name}-root
URL: http://www.pythoncad.org/
Packager: D. Scott Barninger <barninger at fairfieldcomputers dot com>
BuildArchitectures: noarch

%if %{rhel}
BuildRequires: python >= %{pyver}
Requires: python >= %{pyver}
Requires: pygtk2 >= 1.99.16
Requires: libxml2-python
%endif
%if %{suse}
BuildRequires: python >= %{pyver}
Requires: python >= %{pyver}
Requires: python-gtk >= 2.0
Requires: python-xml
%endif
%if %{mdk}
BuildRequires: python >= %{pyver}
Requires: python >= %{pyver}
Requires: pygtk2.0
Requires: libxml2-python
%endif


%description
PythonCAD is a CAD package written, surprisingly enough, in Python. 
The PythonCAD project aims to produce a scriptable, open-source, easy to use 
CAD package for Linux, the various flavors of BSD Unix, commercial Unix, and 
other platforms to which someone who is interested ports the program. Work 
began on PythonCAD in July, 2002, and the first public release was on 
December 21, 2002.


%prep

%setup -q -n %{name}-%{_version}
#%patch -p0

%build

%install

[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "$RPM_BUILD_ROOT"

python setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/etc/pythoncad
mkdir -p $RPM_BUILD_ROOT/usr/share/pixmaps
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
cp gtkpycad.py $RPM_BUILD_ROOT/usr/bin/
cp prefs.py $RPM_BUILD_ROOT/etc/pythoncad/
cp pythoncad.desktop $RPM_BUILD_ROOT/usr/share/applications/
cp gtkpycad.png $RPM_BUILD_ROOT/usr/share/pixmaps/
chmod 755 $RPM_BUILD_ROOT/usr/bin/gtkpycad.py
chmod 644 $RPM_BUILD_ROOT/etc/pythoncad/prefs.py
chmod 644 $RPM_BUILD_ROOT/usr/share/applications/pythoncad.desktop
chmod 644 $RPM_BUILD_ROOT/usr/share/pixmaps/gtkpycad.png


%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "$RPM_BUILD_ROOT"

%files
%defattr(-,root,root)
/usr/%{_lib}/python%pyver/site-packages/PythonCAD/*
/usr/bin/gtkpycad.py
/etc/pythoncad/prefs.py
/usr/share/applications/pythoncad.desktop
/usr/share/pixmaps/gtkpycad.png

%post

%preun

%changelog
* Fri Dec 01 2006 D. Scott Barninger <barninger at fairfieldcomputers.com>
- add prefix specification to install
* Sun Oct 01 2006 D. Scott Barninger <barninger at fairfieldcomputers.com>
- release 0.1.34
* Wed Feb 1 2006 Art Haas <ahaas@airmail.net>
- Update version numbers
* Sat Jan 27 2006 D. Scott Barninger <barninger at fairfieldcomputers.com>
- release 0.1.27
* Sat Jan 15 2005 D. Scott Barninger <barninger at fairfieldcomputers.com>
- setup version strings so we don't have to repackage source
* Fri Oct 15 2004 D. Scott Barninger <barninger at fairfieldcomputers.com>
- initial spec file
