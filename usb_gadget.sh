#!/bin/bash
###
 # @Author: xxchong 2106997706@qq.com
 # @Date: 2024-10-10 11:51:28
 # @LastEditors: xxchong 2106997706@qq.com
 # @LastEditTime: 2024-10-18 11:32:06
 # @FilePath: \QTDesigner\usb_gadget.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 

# cd /sys/kernel/config/usb_gadget/
# mkdir -p isticktoit
# cd isticktoit

# echo 0x1d6b > idVendor # Linux Foundation
# echo 0x0104 > idProduct # Multifunction Composite Gadget
# echo 0x0100 > bcdDevice # v1.0.0
# echo 0x0200 > bcdUSB # USB2

# mkdir -p strings/0x409
# echo "fedcba9876543210" > strings/0x409/serialnumber
# echo "Raspberry Pi" > strings/0x409/manufacturer
# echo "PI3 USB Device" > strings/0x409/product

# mkdir -p configs/c.1/strings/0x409
# echo "Config 1: ECM network" > configs/c.1/strings/0x409/configuration
# echo 250 > configs/c.1/MaxPower

# # 鼠标功能（支持相对和绝对模式）
# mkdir -p functions/hid.usb0
# echo 2 > functions/hid.usb0/protocol
# echo 1 > functions/hid.usb0/subclass
# echo 6 > functions/hid.usb0/report_length
# echo -ne \\x05\\x01\\x09\\x02\\xA1\\x01\\x85\\x01\\x09\\x01\\xA1\\x00\\x05\\x09\\x19\\x01\\x29\\x03\\x15\\x00\\x25\\x01\\x95\\x03\\x75\\x01\\x81\\x02\\x95\\x01\\x75\\x05\\x81\\x03\\x05\\x01\\x09\\x30\\x09\\x31\\x15\\x81\\x25\\x7F\\x75\\x08\\x95\\x02\\x81\\x06\\xC0\\x85\\x02\\x09\\x01\\xA1\\x00\\x05\\x09\\x19\\x01\\x29\\x03\\x15\\x00\\x25\\x01\\x95\\x03\\x75\\x01\\x81\\x02\\x95\\x01\\x75\\x05\\x81\\x03\\x05\\x01\\x09\\x30\\x09\\x31\\x16\\x00\\x00\\x26\\xFF\\x7F\\x75\\x10\\x95\\x02\\x81\\x02\\xC0\\xC0 > functions/hid.usb0/report_desc
# ln -s functions/hid.usb0 configs/c.1/

# # 键盘功能（保持不变）
# mkdir -p functions/hid.usb1
# echo 1 > functions/hid.usb1/protocol
# echo 1 > functions/hid.usb1/subclass
# echo 8 > functions/hid.usb1/report_length
# echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb1/report_desc
# ln -s functions/hid.usb1 configs/c.1/

# # 启用设备
# ls /sys/class/udc > UDC


#!/bin/bash

# Configures USB gadgets per: https://www.kernel.org/doc/Documentation/usb/gadget_configfs.txt

# Exit on first error.
set -e

# Echo commands to stdout.
set -x

# Treat undefined environment variables as errors.
set -u

modprobe libcomposite

# https://eleccelerator.com/tutorial-about-usb-hid-report-descriptors/


cd /sys/kernel/config/usb_gadget/
mkdir -p g1
cd g1

echo 0x1d6b > idVendor  # Linux Foundation
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x0100 > bcdDevice # v1.0.0
echo 0x0200 > bcdUSB    # USB2

STRINGS_DIR="strings/0x409"
mkdir -p "$STRINGS_DIR"
echo "6b65796d696d6570690" > "${STRINGS_DIR}/serialnumber"
echo "tinypilot" > "${STRINGS_DIR}/manufacturer"
echo "Multifunction USB Device" > "${STRINGS_DIR}/product"

# Keyboard
KEYBOARD_FUNCTIONS_DIR="functions/hid.keyboard"
mkdir -p "$KEYBOARD_FUNCTIONS_DIR"
echo 1 > "${KEYBOARD_FUNCTIONS_DIR}/protocol" # Keyboard
echo 1 > "${KEYBOARD_FUNCTIONS_DIR}/subclass" # Boot interface subclass
echo 8 > "${KEYBOARD_FUNCTIONS_DIR}/report_length"
# Write the report descriptor
D=$(mktemp)

{
  echo -ne \\x05\\x01       # Usage Page (Generic Desktop Ctrls)
  echo -ne \\x09\\x06       # Usage (Keyboard)
  echo -ne \\xA1\\x01       # Collection (Application)
  echo -ne \\x05\\x08       #   Usage Page (LEDs)
  echo -ne \\x19\\x01       #   Usage Minimum (Num Lock)
  echo -ne \\x29\\x03       #   Usage Maximum (Scroll Lock)
  echo -ne \\x15\\x00       #   Logical Minimum (0)
  echo -ne \\x25\\x01       #   Logical Maximum (1)
  echo -ne \\x75\\x01       #   Report Size (1)
  echo -ne \\x95\\x03       #   Report Count (3)
  echo -ne \\x91\\x02       #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
  echo -ne \\x09\\x4B       #   Usage (Generic Indicator)
  echo -ne \\x95\\x01       #   Report Count (1)
  echo -ne \\x91\\x02       #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
  echo -ne \\x95\\x04       #   Report Count (4)
  echo -ne \\x91\\x01       #   Output (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
  echo -ne \\x05\\x07       #   Usage Page (Kbrd/Keypad)
  echo -ne \\x19\\xE0       #   Usage Minimum (0xE0)
  echo -ne \\x29\\xE7       #   Usage Maximum (0xE7)
  echo -ne \\x95\\x08       #   Report Count (8)
  echo -ne \\x81\\x02       #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
  echo -ne \\x75\\x08       #   Report Size (8)
  echo -ne \\x95\\x01       #   Report Count (1)
  echo -ne \\x81\\x01       #   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
  echo -ne \\x19\\x00       #   Usage Minimum (0x00)
  echo -ne \\x29\\x91       #   Usage Maximum (0x91)
  echo -ne \\x26\\xFF\\x00  #   Logical Maximum (255)
  echo -ne \\x95\\x06       #   Report Count (6)
  echo -ne \\x81\\x00       #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
  echo -ne \\xC0            # End Collection
} >> "$D"
cp "$D" "${KEYBOARD_FUNCTIONS_DIR}/report_desc"

# Mouse Relative
MOUSE_RELATIVE_FUNCTIONS_DIR="functions/hid.mouse_relative"
mkdir -p "$MOUSE_RELATIVE_FUNCTIONS_DIR"
echo 0 > "${MOUSE_RELATIVE_FUNCTIONS_DIR}/protocol"
echo 0 > "${MOUSE_RELATIVE_FUNCTIONS_DIR}/subclass"
echo 7 > "${MOUSE_RELATIVE_FUNCTIONS_DIR}/report_length"
# Write the report descriptor
D=$(mktemp)
{
echo -ne \\x05\\x01      # USAGE_PAGE (Generic Desktop)
echo -ne \\x09\\x02      # USAGE (Mouse)
echo -ne \\xA1\\x01      # COLLECTION (Application)
                         #   8-buttons
echo -ne \\x05\\x09      #   USAGE_PAGE (Button)
echo -ne \\x19\\x01      #   USAGE_MINIMUM (Button 1)
echo -ne \\x29\\x08      #   USAGE_MAXIMUM (Button 8)
echo -ne \\x15\\x00      #   LOGICAL_MINIMUM (0)
echo -ne \\x25\\x01      #   LOGICAL_MAXIMUM (1)
echo -ne \\x95\\x08      #   REPORT_COUNT (8)
echo -ne \\x75\\x01      #   REPORT_SIZE (1)
echo -ne \\x81\\x02      #   INPUT (Data,Var,Abs)

                         #   x,y relative coordinates
echo -ne \\x05\\x01      #   USAGE_PAGE (Generic Desktop)
echo -ne \\x09\\x30      #   USAGE (X)
echo -ne \\x09\\x31      #   USAGE (Y)
echo -ne \\x15\\x81      #   LOGICAL_MINIMUM (-127)
echo -ne \\x25\\x7f      #   LOGICAL_MAXIMUM (127)
echo -ne \\x75\\x08      #   REPORT_SIZE (16)
echo -ne \\x95\\x02      #   REPORT_COUNT (2)
echo -ne \\x81\\x06      #   INPUT (Data,Var,Rel)

                         #   vertical wheel
echo -ne \\x09\\x38      #   USAGE (wheel)
echo -ne \\x15\\x81      #   LOGICAL_MINIMUM (-127)
echo -ne \\x25\\x7F      #   LOGICAL_MAXIMUM (127)
echo -ne \\x75\\x08      #   REPORT_SIZE (8)
echo -ne \\x95\\x01      #   REPORT_COUNT (1)
echo -ne \\x81\\x06      #   INPUT (Data,Var,Rel)
                         #   horizontal wheel
echo -ne \\x05\\x0C      #   USAGE_PAGE (Consumer Devices)
echo -ne \\x0A\\x38\\x02 #   USAGE (AC Pan)
echo -ne \\x15\\x81      #   LOGICAL_MINIMUM (-127)
echo -ne \\x25\\x7F      #   LOGICAL_MAXIMUM (127)
echo -ne \\x75\\x08      #   REPORT_SIZE (8)
echo -ne \\x95\\x01      #   REPORT_COUNT (1)
echo -ne \\x81\\x06      #   INPUT (Data,Var,Rel)
echo -ne \\xC0           # END_COLLECTION
} >> "$D"
cp "$D" "${MOUSE_RELATIVE_FUNCTIONS_DIR}/report_desc"

# Mouse Absolute
MOUSE_ABSOLUTE_FUNCTIONS_DIR="functions/hid.mouse_absolute"
mkdir -p "$MOUSE_ABSOLUTE_FUNCTIONS_DIR"
echo 0 > "${MOUSE_ABSOLUTE_FUNCTIONS_DIR}/protocol"
echo 0 > "${MOUSE_ABSOLUTE_FUNCTIONS_DIR}/subclass"
echo 7 > "${MOUSE_ABSOLUTE_FUNCTIONS_DIR}/report_length"
# Write the report descriptor
D=$(mktemp)
{
echo -ne \\x05\\x01      # USAGE_PAGE (Generic Desktop)
echo -ne \\x09\\x02      # USAGE (Mouse)
echo -ne \\xA1\\x01      # COLLECTION (Application)
                         #   8-buttons
echo -ne \\x05\\x09      #   USAGE_PAGE (Button)
echo -ne \\x19\\x01      #   USAGE_MINIMUM (Button 1)
echo -ne \\x29\\x08      #   USAGE_MAXIMUM (Button 8)
echo -ne \\x15\\x00      #   LOGICAL_MINIMUM (0)
echo -ne \\x25\\x01      #   LOGICAL_MAXIMUM (1)
echo -ne \\x95\\x08      #   REPORT_COUNT (8)
echo -ne \\x75\\x01      #   REPORT_SIZE (1)
echo -ne \\x81\\x02      #   INPUT (Data,Var,Abs)


                         #   x,y absolute coordinates
echo -ne \\x05\\x01      #   USAGE_PAGE (Generic Desktop)
echo -ne \\x09\\x30      #   USAGE (X)
echo -ne \\x09\\x31      #   USAGE (Y)
echo -ne \\x15\\x00      #   LOGICAL_MINIMUM (0)
echo -ne \\x26\\xff\\x7f #   LOGICAL_MAXIMUM (65535)
echo -ne \\x75\\x10      #   REPORT_SIZE (16)
echo -ne \\x95\\x02      #   REPORT_COUNT (2)
echo -ne \\x81\\x02      #   INPUT (Data,Var,RAbs)

                         #   vertical wheel
echo -ne \\x09\\x38      #   USAGE (wheel)
echo -ne \\x15\\x81      #   LOGICAL_MINIMUM (-127)
echo -ne \\x25\\x7F      #   LOGICAL_MAXIMUM (127)
echo -ne \\x75\\x08      #   REPORT_SIZE (8)
echo -ne \\x95\\x01      #   REPORT_COUNT (1)
echo -ne \\x81\\x06      #   INPUT (Data,Var,Rel)
                         #   horizontal wheel
echo -ne \\x05\\x0C      #   USAGE_PAGE (Consumer Devices)
echo -ne \\x0A\\x38\\x02 #   USAGE (AC Pan)
echo -ne \\x15\\x81      #   LOGICAL_MINIMUM (-127)
echo -ne \\x25\\x7F      #   LOGICAL_MAXIMUM (127)
echo -ne \\x75\\x08      #   REPORT_SIZE (8)
echo -ne \\x95\\x01      #   REPORT_COUNT (1)
echo -ne \\x81\\x06      #   INPUT (Data,Var,Rel)
echo -ne \\xC0           # END_COLLECTION
} >> "$D"
cp "$D" "${MOUSE_ABSOLUTE_FUNCTIONS_DIR}/report_desc"

CONFIG_INDEX=1
CONFIGS_DIR="configs/c.${CONFIG_INDEX}"
mkdir -p "$CONFIGS_DIR"
echo 250 > "${CONFIGS_DIR}/MaxPower"

CONFIGS_STRINGS_DIR="${CONFIGS_DIR}/strings/0x409"
mkdir -p "$CONFIGS_STRINGS_DIR"
echo "Config ${CONFIG_INDEX}: ECM network" > "${CONFIGS_STRINGS_DIR}/configuration"

ln -s "$KEYBOARD_FUNCTIONS_DIR" "${CONFIGS_DIR}/"
ln -s "$MOUSE_RELATIVE_FUNCTIONS_DIR" "${CONFIGS_DIR}/"
ln -s "$MOUSE_ABSOLUTE_FUNCTIONS_DIR" "${CONFIGS_DIR}/"
ls /sys/class/udc > UDC

chmod 777 /dev/hidg0 # Keyboard
chmod 777 /dev/hidg1 # Mouse Relative
chmod 777 /dev/hidg2 # Mouse Absolute