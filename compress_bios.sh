#!/bin/bash
# NOTE: Perhaps one day we can do this with GitHub Actions,
# https://github.com/marketplace/actions/image-actions looks promising but doesn't
# support resizeing yet and overwrites the existing image.

# {jpg,png,jpeg,webp}

rm -rf "assets/images/bios_compressed"
mkdir -p "assets/images/bios_compressed"

for filename in "assets/images/bios"/*.{jpg,png,jpeg}
do
  basename=$(basename ${filename%.*})
  echo "$basename"
  gm convert $filename -resize 200x200 -compress jpeg +profile "*" -quality 75 "assets/images/bios_compressed/$basename.jpg"
  gm convert $filename -resize 200x200 -compress webp +profile "*" -quality 85 "assets/images/bios_compressed/$basename.webp"
done

