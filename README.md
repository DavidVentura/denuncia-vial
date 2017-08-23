## Dependencies

* BeautifulSoup
* xmltodict
* exifread
* requests

## Features

* exif parsing
  * auto rotation
  * get time
* Reduce image quality on upload
* Generate link to check report status

## Usage
Talk to your bot.

* /start
* (image 1)
* (image 2)
* plate
* /confirm

![](images/img1.png)
![](images/img2.png)
![](images/gmail.png)

## Configuration

### lib/data.json

Copy `lib/data.json.example` and set the corresponding values.

### telegram.json
Copy `telegram.json.example` and set the authorized users' ids and 
your bot's token.

## Things to fix:

* Images are downloaded, written to file and read from the file.
