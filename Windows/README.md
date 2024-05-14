# Project Gameface
Project Gameface helps gamers control their mouse cursor using their head movement and facial gestures.


# Download
1. Download the program from [Release section](../../releases/)
2. Run `run_app.exe`


# Python application

## Installation
> Environment
>- Windows  
>- Python 3.9
```
pip install -r requirements.txt
```

## Quick start
1. Run main application
    ```
    python run_app.py
    ```


# Configs
## Basic config

>[cursor.json](configs/default/cursor.json)  

|           |                                       |
|-----------|---------------------------------------|
| camera_id | Default camera index on your machine. |
| tracking_vert_idxs | Tracking points for controlling cursor ([see](assets/images/uv_unwrap_full.png)) |
| spd_up    | Cursor speed in the upward direction  |
| spd_down  | Cursor speed in downward direction    |
| spd_left  | Cursor speed in left direction        |
| spd_right | Cursor speed in right direction       |
| pointer_smooth  | Amount of cursor smoothness           |
| shape_smooth  | Reduces the flickering of the action           |
| hold_trigger_ms  | Hold action trigger delay in milliseconds           |
| auto_play  | Automatically begin playing when you launch the program           |
| mouse_acceleration  | Make the cursor move faster when the head moves quickly        |
| use_transformation_matrix  | Control cursor using head direction (tracking_vert_idxs will be ignored)   |
 

## Keybinds configs
>[mouse_bindings.json](configs/default/mouse_bindings.json)  
>[keyboard_bindings.json](configs/default/keyboard_bindings.json) 

The config parameters for keybinding configuration are in this structure.
```
gesture_name: [device_name, action_name, threshold, trigger_type]
```


|              |                                                                                           |
|--------------|-------------------------------------------------------------------------------------------|
| gesture_name | Face expression name, see the [list](src/shape_list.py#L16)       |
| device_name  | "mouse" or "keyboard"                                                                     |
| action_name  | "left", "right" and "middle" for mouse. "" for keyboard, for instance, "w" for the W key. |
| threshold    | The action trigger threshold has values ranging from 0.0 to 1.0.        |
| trigger_type | Action trigger type, use "single" for a single trigger, "hold" for ongoing action.                                 |





# Build
```
    pyinstaller build.spec
```

