**yanesdkTool**

small command line tool for working with yanesdk (\*.dat) files, some .dat files need .lst file (which contains necessary information for extraction) which not currently supported, only view mode is supported

**Usage: python exshikidat.py [OPTIONS]**

Options:

>>_-u, --unpack_ for unpack mode. default is view mode

>>_-p, --pack_ for pack mode

>>_-f, --file_ file path to unpack/pack

>>_-d, --directory_ directory path to unpack/pack

>>_--help_ Show this message and exit.

Requirements:

>Python 3.7 or later with modules:

>>- bytesfunc
>>- click

Reference:

- https://github.com/morkt/GARbro/blob/master/ArcFormats/YaneSDK/ArcHibiki.cs