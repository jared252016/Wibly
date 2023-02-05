# Wibly
Wibly is an automated scanner and media consumption tool. Think of it like an AI driven web spider for tube sites. It can process thumbnails for videos and run various kinds of detction algorithms on them, such as phash against a video frame, or machine learning style recognition.

## How It Works
Wibly works by ingesting yaml files that contain 3 main categories: parsers, detectors, and commands.

### Parsers
Parsers allow you to locate elements on the page. It works similar to youtube-dl, however instead of it being powered by regex it uses CSS selectors and html tags. 

Here is an example parser:
```
parser:
    item: "div.item.item-col" # We want all divs with the class .item
    video_id:
      item:
        - tag: parent # We can also set the tag to parent, to use the div.item tag
        - attr: data-video-id # Here we get the attribute data-video-id
        - attr-type: int # Here we tell it that the value for data-video-id should be an integer. In Python this will mean int(val) was called. Supports int and str, default is str.
    title: # Set our title property
      item: # Tell it the parent is item
        - tag: a # Tag
        - class: title # Class
        - attr: text # Attribute
    video_thumbnail: 
      item:
        - tag: img
        - attr: data-preview
    image_thumbnail: 
      item:
        - tag: img
        - attr: src
    video_url:
      item:
        - tag: a
        - class: image
        - attr: href
    next_page_url: 
      global: # For global elements, tell it to use global
        - tag: li
        - class: next
        - attr: a.href
 ```
 The base item is the "div.item.item-col" and it serves as the container for the other items, which is specified to the other items by specifying "item" under the name of the element, or property that it creates. This more or less returns a dictionary of properties to the detector which can process the data. The names of the properties in this example would be video_id, title, video_thumbnail, image_thumbnail, video_url, and the global (not under item), next_page_url. 
 
 ### Detectors

Currently the only active and working detector is the string detector which just allows you to match based on string contains.

Other detectors may potentially include:
- Face Detection / Recognition
- Skin Color Detection
- Age Detection
- Scene Recognition
- Object Recognition

An example for detectors is as follows:
```
detectors:
    title: # name of the detector
      priority: 1 # NYI - Not Yet Implemented
      detector: detectors.gnd_string
      runs_on: 
        - title: parser.title
      exec: download-video
    #skin: # The internal name of the detector. Use this to reference the detector later on, such as detectors.skin
    #  detector: detectors.gnd_skin # The actual class name of the detector to use
    #  cache: cache/
    #  runs_on: # One or more properties to pass into the detector. Properties keep their names from parser, and the detector may require them to be named according to a specific standard.
    #    - video: parser.video_thumbnail # An example property being passed in. 
    #
    #  exec: download-critera # The command to execute on completion
  # Commands are executable actions that can be triggered on the on-complete event of a detector (exec). Commands consist of multiple components as well as critera that determines
  # if the command is actually run or not, based on the detectors. 
```
As you can see, there is a detector called title that executes the gnd_string detector for "in-string" comparison. It runs on the parser.title which is the property set in the parsers above. After it runs it's detection, it executes a command called *download-video*. In a additional example, we could use skin detection to determine the skin color summary within the video thumbnail. This would be useful if we were searching for all asians, or all whites, or looking for foreign media on a tube site.

### Commands
Lastly, we have a command that gets executed. Currently there is only one operational command and that is *youtube-dl*, but in theory you would be able to perform other actions as well, such as adding the item to a database for collecting statistics.

Here we have an example of the commands section:
```
commands:
    download-video: # The name of the command to run, which is what is used elsewhere in the yaml configuration.
      action: youtube-dl # The action to take. These are internal actions built into gn_auto. 
      cache: cache/
      location: /path/to/my/files # Location to store downloaded files
      args: # Pass arguments to the action
        - no_check_certificate: True # We pass in no-check-certificate, which is translated to --no-check-certificate and passed to the youtube-dl binary.
        - url: parser.video_url # We pass in our url, telling it to use the value from parser.video_url.
        # - local_file=commands.download-video.out_file # Commands can add return values to the list of properties as well. Daisy chaining commands can use this data like so.
      critera: # The critera to determine whether or not the action runs. The critera in this section all use the "or" operator. Any "and" operators should be done as a critera.
        apples:
          detector: detectors.title
          mode: or
          modify: lower
          require:
            - apple
            - apples
            - green apple
            - red apple
        bananas:
          detector: detectors.title
          mode: or
          modify: lower
          require:
            - bananas
            - banana
        oranges:
          detector: detectors.title # the detector being used
          mode: single # The mode is set to single, so that only one require value will be used.
          modify: upper # A modify option is passed through to tell the detector to uppercase the return value
          require:
            - ORANGE
      exec: "update-database" # Supports calling an additional command upon the completion of a command, passing in all properties including the path to the newly outputted files.
    update-database: # A second command that runs after the first command by daisy chaining with the exec property.
      action: media-insert-update # The media-insert-update action inserts a new row into a table or updates it if it already exists, automatically populating filesize and the other properties not specified.
      args:
        - primary_key: url # The primary key argument tells the SQL insert/update to use this field as the primary key
        - title: parser.title # Pass in the title parameter into the query
        - url: parser.video_url # Pass in the url parameter into the query
        - download_url: commands.download-video.download_url # Pass in the previous command's download_url property (from youtube-dl)
        - download_file: commands.download-video.out_file # Pass in the previous command's out_file property (from youtube-dl)
```
