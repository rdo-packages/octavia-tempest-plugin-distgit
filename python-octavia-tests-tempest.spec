%{!?upstream_version: %global upstream_version %{commit}}
%global commit 51e91b4dfe9bed364912034b7f8a51528b46fd84
%global shortcommit %(c=%{commit}; echo ${c:0:7})
# DO NOT REMOVE ALPHATAG
%global alphatag .%{shortcommit}git

%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 0

%if 0%{?fedora}
%global with_python3 1
%endif

%global common_desc \
This package contains Tempest tests to cover the Octavia project. \
Additionally it provides a plugin to automatically load these tests into Tempest.


Name:       python-%{service}-tests-tempest
Version:    1.1.0
Release:    1%{?alphatag}%{?dist}
Summary:    Tempest Integration of Octavia Project
License:    ASL 2.0
URL:        https://git.openstack.org/cgit/openstack/%{plugin}/

Source0:    http://github.com/openstack/%{plugin}/archive/%{commit}.tar.gz#/%{plugin}-%{shortcommit}.tar.gz

BuildRequires:  git
BuildRequires:  openstack-macros

%description
%{common_desc}

%package -n python-%{service}-tests-tempest-golang
Summary:        python2-%{service}-tests-tempest golang files

BuildRequires:  golang
BuildRequires:  glibc-static

%description -n python-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python2-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python2-%{service}-tests-tempest}
BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools

Obsoletes:   python-octavia-tests < 2.0.0

Requires:       python-%{service}-tests-tempest-golang = %{version}-%{release}
Requires:       python2-pbr >= 2.0
Requires:       python2-oslotest >= 1.10.0
Requires:       python2-tempest >= 1:17.2.0
Requires:       python2-tenacity >= 3.2.1
Requires:       python2-dateutil
Requires:       python-ipaddress
Requires:       python2-oslo-config
Requires:       python2-oslo-log
Requires:       python2-oslo-utils
Requires:       python2-requests
Requires:       python2-six
Requires:       python2-cryptography >= 2.1
Requires:       python2-barbicanclient >= 4.5.2
Requires:       python2-pyOpenSSL >= 17.1.0
Requires:       python2-oslo-serialization >= 2.18.0

%description -n python2-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

BuildRequires:  python2-sphinx
BuildRequires:  python2-oslo-sphinx
BuildRequires:  python2-openstackdocstheme
# Required for documentation build
BuildRequires:  python2-oslo-config
BuildRequires:  python2-tempest

%description -n python-%{service}-tests-tempest-doc
It contains the documentation for the Octavia tempest plugin.
%endif

%if 0%{?with_python3}
%package -n python3-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python3-%{service}-tests-tempest}


BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools

Requires:       python-%{service}-tests-tempest-golang = %{version}-%{release}
Requires:       python3-pbr >= 2.0
Requires:       python3-oslotest >= 1.10.0
Requires:       python3-tempest >= 1:17.2.0
Requires:       python3-tenacity >= 3.2.1
Requires:       python3-dateutil
Requires:       python3-oslo-config
Requires:       python3-oslo-log
Requires:       python3-oslo-utils
Requires:       python3-requests
Requires:       python3-six
Requires:       python3-cryptography >= 2.1
Requires:       python3-barbicanclient >= 4.5.2
Requires:       python3-pyOpenSSL >= 17.1.0
Requires:       python3-oslo-serialization >= 2.18.0

%description -n python3-%{service}-tests-tempest
%{common_desc}
%endif

%prep
%autosetup -n %{plugin}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup
# Remove bundled egg-info
rm -rf %{module}.egg-info

%build
%if 0%{?with_python3}
%py3_build
%endif
%py2_build

# Generate octavia test httpd binary from httpd.go
pushd %{module}/contrib/httpd
 go build -ldflags '-linkmode external -extldflags -static' -o %{plugin}-tests-httpd httpd.go
popd

# Generate Docs
%if 0%{?with_doc}
export PYTHONPATH=.
sphinx-build -W -b html doc/source doc/build/html
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%if 0%{?with_python3}
%py3_install
%endif
%py2_install

# Move httpd binary to proper place
install -d -p %{buildroot}%{_libexecdir}
install -p -m 0755 %{module}/contrib/httpd/%{plugin}-tests-httpd %{buildroot}%{_libexecdir}/%{plugin}-tests-httpd
ln -s -f %{_libexecdir}/%{plugin}-tests-httpd %{buildroot}%{python2_sitelib}/%{module}/contrib/httpd/httpd.bin
%if 0%{?with_python3}
ln -s -f %{_libexecdir}/%{plugin}-tests-httpd %{buildroot}%{python3_sitelib}/%{module}/contrib/httpd/httpd.bin
%endif

# Remove httpd.go code
rm  %{buildroot}%{python2_sitelib}/%{module}/contrib/httpd/httpd.go

# And for python3
%if 0%{?with_python3}
rm  %{buildroot}%{python3_sitelib}/%{module}/contrib/httpd/httpd.go
%endif

%files -n python-%{service}-tests-tempest-golang
%{_libexecdir}/%{plugin}-tests-httpd
%{python2_sitelib}/%{module}/contrib/httpd/httpd.bin
%if 0%{?with_python3}
%{python3_sitelib}/%{module}/contrib/httpd/httpd.bin
%endif

%files -n python2-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%exclude %{python2_sitelib}/%{module}/contrib/httpd/httpd.bin
%{python2_sitelib}/%{module}
%{python2_sitelib}/*.egg-info

%if 0%{?with_python3}
%files -n python3-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%exclude %{python3_sitelib}/%{module}/contrib/httpd/httpd.bin
%{python3_sitelib}/%{module}
%{python3_sitelib}/*.egg-info
%endif

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
* Tue Jul 16 2019 RDO <dev@lists.rdoproject.org> 1.1.0-1.51e91b4git
- Update to 1.1.0

* Fri Oct 12 2018 Carlos Goncalves <cgoncalves@redhat.com> 0.0.1-0.3.51e91b4git
- Fix httpd binary location to expected path by tests

* Thu Apr 12 2018 Yatin Karel <ykarel@redhat.com> - 0.0.1-0.2.51e91b4dgit
- Fix spec for updated scenario tests

* Mon Feb 19 2018 Chandan Kumar <chkumar@redhat.com> 0.0.1-0.1.019e4eb9git
- Update to pre-release 0.0.1 (019e4eb90f2733783025ed73ae5dfe1f165c5d97)
