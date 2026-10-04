%global forgeurl https://github.com/Map1en/VRCX-0

# Upstream release profile is fat LTO, one codegen unit, opt-level "s".
# Fedora's %%build_rustflags defaults to opt-level 3, full debuginfo and one
# codegen unit, which OOM COPR builders together with fat LTO. Keep size-oriented
# optimization, thin LTO, and lighter debuginfo.
%global rustflags_opt_level s
%global rustflags_debuginfo 1
%global rustflags_codegen_units 8

# rustc links bundled C (libwebp-sys and others) with ld.bfd and does not run
# GCC's LTO plugin. Fedora's -flto=auto leaves WebPSafeMalloc and friends as
# LTO-only symbols, so the final link fails with undefined references.
%global _lto_cflags %{nil}

Name:           vrcx-0
Version:        2.31.0
Release:        1%{?dist}
Summary:        Fast, lightweight companion for VRChat

License:        GPL-3.0-only
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/refs/tags/v%{version}.tar.gz
Source1:        vrcx-0.metainfo.xml
Source2:        VRCX-0.desktop

# Linux CI and the upstream CPU target are x86_64 / x86-64-v2.
ExclusiveArch:  x86_64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  pkgconf-pkg-config
BuildRequires:  patchelf
BuildRequires:  file
BuildRequires:  git-core
BuildRequires:  perl-interpreter
BuildRequires:  python3
BuildRequires:  clang
BuildRequires:  clang-devel
BuildRequires:  nodejs24
BuildRequires:  nodejs24-devel
BuildRequires:  nodejs24-npm
BuildRequires:  nodejs24-npm-bin
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  gtk3-devel
BuildRequires:  libayatana-appindicator-gtk3-devel
BuildRequires:  libsoup3-devel
BuildRequires:  javascriptcoregtk4.1-devel
BuildRequires:  openssl-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  librsvg2-devel
BuildRequires:  libxdo-devel
BuildRequires:  dbus-devel
BuildRequires:  desktop-file-utils

# Tray support dlopens ayatana; rpm cannot see that from DT_NEEDED.
Requires:       libayatana-appindicator3.so.1()(64bit)
Requires:       hicolor-icon-theme
# VR overlay loads this at runtime. Missing loader only disables the overlay.
Recommends:     libopenxr_loader.so.1()(64bit)

# Tauri resolves bundled resources from /usr/lib/<product>, not %%{_libdir}.
%global tauri_resourcedir /usr/lib/VRCX-0

%description
VRCX-0 is a desktop companion for VRChat. It shows where friends are, keeps a
history of people and worlds, and manages favorites.

This package is built from the upstream tag. The in-app updater is turned off
so upgrades come from this repository with dnf, instead of replacing the files
out from under the package manager.

%prep
%autosetup -n VRCX-0-%{version} -p1

%build
# Fedora exports RUSTFLAGS before this script. Those flags replace
# .cargo/config.toml, so put the upstream CPU baseline and the build-id back.
export RUSTFLAGS="${RUSTFLAGS:-} -Ctarget-cpu=x86-64-v2 -Clink-arg=-Wl,-z,relro -Clink-arg=-Wl,-z,now -Clink-arg=-Wl,--build-id=sha1"
export CARGO_PROFILE_RELEASE_LTO=thin
export CARGO_HOME="%{_builddir}/.cargo"
export LIBCLANG_PATH="%{_libdir}"
export HUSKY=0
export VRCX_0_DISABLE_UPDATE_CHECK=1
export npm_config_cache="%{_builddir}/.npm"
export NODE_OPTIONS="${NODE_OPTIONS:-} --max-old-space-size=4096"
mkdir -p "$CARGO_HOME" "$npm_config_cache"

npm ci --no-audit --no-fund
npm run tauri:build -- \
    --no-sign \
    --no-bundle \
    --config src-tauri/tauri.linux.conf.json \
    -- --locked

%install
install -Dm0755 target/release/vrcx-0 %{buildroot}%{_bindir}/vrcx-0
install -Dm0644 LICENSE %{buildroot}%{tauri_resourcedir}/LICENSE
install -Dm0644 LICENSES/MIT.txt %{buildroot}%{tauri_resourcedir}/LICENSES/MIT.txt
install -Dm0644 src-tauri/resources/licenses/THIRD_PARTY_NOTICES.txt \
    %{buildroot}%{tauri_resourcedir}/licenses/THIRD_PARTY_NOTICES.txt

install -Dm0644 src-tauri/icons/32x32.png \
    %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/vrcx-0.png
install -Dm0644 src-tauri/icons/64x64.png \
    %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/vrcx-0.png
install -Dm0644 src-tauri/icons/128x128.png \
    %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/vrcx-0.png
install -Dm0644 src-tauri/icons/128x128@2x.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/vrcx-0.png

desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE2}
install -Dm0644 %{SOURCE1} %{buildroot}%{_metainfodir}/io.github.map1en.vrcx0.metainfo.xml

%files
%license LICENSE
%doc README.md
%{_bindir}/vrcx-0
%{tauri_resourcedir}/
%{_datadir}/applications/VRCX-0.desktop
%{_metainfodir}/io.github.map1en.vrcx0.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/vrcx-0.png

%changelog
* Mon Oct 05 2026 lonelyicer <lonelyicer@qq.com> - 2.31.0-1
- Package VRCX-0 2.31.0 for Fedora COPR
