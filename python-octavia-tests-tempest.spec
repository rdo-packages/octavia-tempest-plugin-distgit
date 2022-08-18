%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 1

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global common_desc \
This package contains Tempest tests to cover the Octavia project. \
Additionally it provides a plugin to automatically load these tests into Tempest.


Name:       python-%{service}-tests-tempest
Version:    XXX
Release:    XXX
Summary:    Tempest Integration of Octavia Project
License:    ASL 2.0
URL:        https://git.openstack.org/cgit/openstack/%{plugin}/

Source0:    http://tarballs.openstack.org/%{plugin}/%{plugin}-%{upstream_version}.tar.gz
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{plugin}/%{plugin}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:  git-core
BuildRequires:  openstack-macros

%description
%{common_desc}

%package -n python3-%{service}-tests-tempest-golang
Summary:        python3-%{service}-tests-tempest golang files
%{?python_provide:%python_provide python3-%{service}-tests-tempest-golang}

BuildRequires:  golang

%description -n python3-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python3-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch
%{?python_provide:%python_provide python3-%{service}-tests-tempest}

BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools

Obsoletes:      python-octavia-tests < 2.0.0

Requires:       python3-%{service}-tests-tempest-golang
Requires:       python3-pbr >= 2.0.0
Requires:       python3-oslotest >= 3.2.0
Requires:       python3-tempest >= 1:18.0.0
Requires:       python3-tenacity >= 4.4.0
Requires:       python3-dateutil >= 2.5.3
Requires:       python3-oslo-config >= 5.2.0
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-utils >= 3.33.0
Requires:       python3-requests >= 2.14.2
Requires:       python3-cryptography >= 2.1
Requires:       python3-barbicanclient >= 4.5.2
Requires:       python3-pyOpenSSL >= 17.1.0
Requires:       python3-oslo-serialization >= 2.18.0
Requires:       python3-keystoneauth1 >= 3.3.0
Requires:       python3-testtools >= 2.2.0
Requires:       python3-httpx
Requires:       python3-h2

%description -n python3-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

BuildRequires:  python3-sphinx
BuildRequires:  python3-sphinxcontrib-apidoc
BuildRequires:  python3-sphinxcontrib-rsvgconverter
BuildRequires:  python3-openstackdocstheme
# Required for documentation build
BuildRequires:  python3-barbicanclient
BuildRequires:  python3-oslo-config
BuildRequires:  python3-tempest
BuildRequires:  python3-tenacity
BuildRequires:  python3-pyOpenSSL

%description -n python-%{service}-tests-tempest-doc
It contains the documentation for the Octavia tempest plugin.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{plugin}-%{upstream_version} -S git

# Let's handle dependencies ourseleves
%py_req_cleanup
# Remove bundled egg-info
rm -rf %{module}.egg-info

%build
%{py3_build}

rm -f %{module}/contrib/test_server/*bin

# Generate octavia test httpd binary from test_server.go
pushd %{module}/contrib/test_server
# gobuild from Fedora's go-rpm-macros https://pagure.io/go-rpm-macros/blob/master/f/rpm/macros.d/macros.go-compilers-golang
# debuginfo missing with compressdwarf https://bugzilla.redhat.com/show_bug.cgi?id=1602096
%global _dwz_low_mem_die_limit 0
CGO_ENABLED=0 GOOS=linux go build -o %{plugin}-tests-httpd -ldflags "-compressdwarf=false ${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n') -extldflags '-static %__global_ldflags'" -a -v -x test_server.go
popd

# Generate Docs
%if 0%{?with_doc}
export PYTHONPATH=.
sphinx-build -b html doc/source doc/build/html
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

# Move httpd binary to a proper place
install -d -p %{buildroot}%{_libexecdir}
install -p -m 0755 %{module}/contrib/test_server/%{plugin}-tests-httpd %{buildroot}%{_libexecdir}/%{plugin}-tests-httpd
ln -s -f %{_libexecdir}/%{plugin}-tests-httpd %{buildroot}%{python3_sitelib}/%{module}/contrib/test_server/test_server.bin

# Remove test_server.go code
rm  %{buildroot}%{python3_sitelib}/%{module}/contrib/test_server/test_server.go

%files -n python3-%{service}-tests-tempest-golang
%{_libexecdir}/%{plugin}-tests-httpd
%{python3_sitelib}/%{module}/contrib/test_server/test_server.bin

%files -n python3-%{service}-tests-tempest
%license LICENSE
%doc README.rst
%exclude %{python3_sitelib}/%{module}/contrib/test_server/test_server.bin
%{python3_sitelib}/%{module}
%{python3_sitelib}/*.egg-info

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
