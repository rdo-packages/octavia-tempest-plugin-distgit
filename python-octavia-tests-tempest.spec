%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global service octavia
%global plugin octavia-tempest-plugin
%global module octavia_tempest_plugin
%global with_doc 1

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order bashate
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global common_desc \
This package contains Tempest tests to cover the Octavia project. \
Additionally it provides a plugin to automatically load these tests into Tempest.


Name:       python-%{service}-tests-tempest
Version:    XXX
Release:    XXX
Summary:    Tempest Integration of Octavia Project
License:    Apache-2.0
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

BuildRequires:  golang

%description -n python3-%{service}-tests-tempest-golang
%{common_desc}

This package contains Octavia tempest golang httpd code.

%package -n python3-%{service}-tests-tempest
Summary: %{summary}
BuildArch:  noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# it requires https[http2] but that's not provided as extra subpackage
# of python3-httpx so i'm adding it manually
Requires: python3-h2

%description -n python3-%{service}-tests-tempest
%{common_desc}

%if 0%{?with_doc}
%package -n python-%{service}-tests-tempest-doc
Summary:        python-%{service}-tests-tempest documentation

BuildArch:  noarch

%description -n python-%{service}-tests-tempest-doc
It contains the documentation for the Octavia tempest plugin.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{plugin}-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# python3-httpx does not provide httpx[http2] so we manage http2 extra manually.
sed -i 's/httpx.*/httpx/g' requirements.txt

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e docs
%else
  %pyproject_buildrequires -R
%endif

%build
%pyproject_wheel

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
%tox -e docs
# remove the sphinx build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

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
%{python3_sitelib}/*.dist-info

%if 0%{?with_doc}
%files -n python-%{service}-tests-tempest-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
