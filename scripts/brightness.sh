
BRI=$(brightnessctl -d intel_backlight get)
BRI=$((BRI*100))
BRI=$((BRI/937))
echo $BRI
case "$1" in
    "up")
          brightnessctl -d intel_backlight set 2%+ 
          volnoti-show -s /usr/share/pixmaps/volnoti/display-brightness-symbolic.svg $BRI
          ;;
  "down")
          brightnessctl -d intel_backlight set 2%-
          volnoti-show -s /usr/share/pixmaps/volnoti/display-brightness-symbolic.svg $BRI
          ;;
esac


exit 0
