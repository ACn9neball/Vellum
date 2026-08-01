# Maintainer: N9neball <youremail@example.com>
pkgname=vellum
pkgver=1.0.4
pkgrel=1
pkgdesc="My custom Python PyQt application built natively for Arch Linux"
arch=('any')
url="https://github.com"
license=('GPL')

# Enforce native system packages for Python and Qt6 bindings
depends=('python' 'python-pyqt6') 

# FIXED: Removed 'src/' directory to stop validation errors. 
# makepkg will look for local individual files alongside the PKGBUILD.
source=('vellum.desktop'
        'icon.png')

# Skip integrity checks since these are your local file assets
sha256sums=('SKIP' 'SKIP')

package() {
  # 1. Create target system directories
  install -d "${pkgdir}/usr/share/${pkgname}"
  install -d "${pkgdir}/usr/bin"

  # 2. FIXED: Pull directly from your active build folder ($startdir) 
  # This recursively grabs your entire local 'src/' module framework cleanly
  cp -r "${startdir}/src/"* "${pkgdir}/usr/share/${pkgname}/"

  # 3. Create a clean system-wide executable binary link inside /usr/bin/
  echo -e "#!/bin/sh\nexec python /usr/share/${pkgname}/main.py \"\$@\"" > "${pkgdir}/usr/bin/${pkgname}"
  chmod 755 "${pkgdir}/usr/bin/${pkgname}"

  # 4. Deploy the desktop UI entry shortcut file
  install -Dm644 "${srcdir}/vellum.desktop" "${pkgdir}/usr/share/applications/${pkgname}.desktop"

  # 5. Copy the icon into the system graphics index
  install -Dm644 "${srcdir}/icon.png" "${pkgdir}/usr/share/pixmaps/${pkgname}.png"
}


