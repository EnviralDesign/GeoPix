# GeoPix v2.0.15525 (2023-10-04) TD v2021.16410

GeoPix is a free and open source real-time lighting control and previz software. It's built in TouchDesigner, with a workflow and UI/UX inspired by 3d animation software.

The primary goal of GeoPix is to unify the process of working with different types of lights, such as led strips, dmx lights, and video surfaces - while streamlining the process of mapping real-time video and generative content onto complex arrays of pixels and lights.

Lastly, GeoPix also aims to bridge the gap between lighting control, and lighting pre-visualization - two tasks that generally require multiple, potentially expensive software & hardware elements.

![GeoPix Image 1](http://www.enviral-design.com/downloads/website_images/GeoPix_GitHub_ReadMe_4.jpg)

![GeoPix Image 2](http://www.enviral-design.com/downloads/website_images/GeoPix_GitHub_ReadMe_5.png)

![GeoPix Image 2](http://www.enviral-design.com/downloads/website_images/GeoPix_GitHub_ReadMe_6.png)

## Post launch gameplan

*06/18/2021* A lot of progress has been made since launch, the Perform tab has it's crucial missing features from launch implemented, many bugs have been fixed, and I keep rolling out new tutorials when I can or on request. The next big push will be to do an optimization pass, another round of bug fixes [discovered recently](https://www.youtube.com/watch?v=KdTKNHLYUJ0), along with more supporting tutorials for big features implemented but not yet documented. 

You'll know we've reached this point when I bump the GeoPix version number to 2.1, and with that will come a fresh new sample project in two variants, a timecoded variant like what you can see in the link above and also a freeplay variant, which is entirely ready to jam on.

## Getting Started
The recommended way of using GeoPix is to download or checkout the entire repository, unzip it if needed, then run the windows batch file called **START_GEOPIX.bat**.

If you already have installed a free or paid TouchDesigner license to your computer, GeoPix will boot right up and be operational after a bit. If you do not have a license, you can get a [free one](https://derivative.ca/) for non commercial work. If you already have a primary older or newer version of Touch that you use for other things, this should not overwrite that install.

Be sure to have an active internet connection during the first run of the batch file, as it will need to download some things, and GeoPix will need to download some python libraries.

### Batch File

If you're curious, or running into issues - here's what the batch file does:

1. Searches computer for an already installed and compatible version of TouchDesigner.
2. Downloads the TouchDesigner installer if not found, then installs it locally to a folder called **.td**
3. GeoPix should launch automatically after install, if not run the batch file again.
4. When GeoPix launches for the first time, or after python requirements have changed, you will see a flash of several cmd windows that are setting up and pip installing libraries to a local python install located in a folder called **.py**

You should not have to worry about any of this, but if you run into issues here please submit an issue and attach the generated logs!

### Installed Files

Everything that is downloaded or installed is done so locally, in the repository folder. You can navigate these yourself, they will start with a **.**

If you accidentally screw up the executable files, copy any relevant project files out, and simply delete the repo and re download/check it out, and run the bat file once more.

## Project Pages

### Software & Project
- [GitHub](https://github.com/EnviralDesign/GeoPix)
- [Issues](https://github.com/EnviralDesign/GeoPix/issues)
- [Roadmap](https://github.com/EnviralDesign/GeoPix/projects)
- [Website](http://www.geopix.io/)
- [ChangeLog](https://github.com/EnviralDesign/GeoPix/blob/main/CHANGE_LOG.txt)

### Learning & Resources
- [Wiki / Docs](https://github.com/EnviralDesign/GeoPix/wiki)
- [Forums](https://github.com/EnviralDesign/GeoPix/discussions)
- [YouTube Channel](https://www.youtube.com/c/LucasMorgan42)
- [Facebook Group](https://www.facebook.com/groups/GeoPixUserGroup)

### Social & Community
- [Facebook Page](https://www.facebook.com/enviraldesign)
- [Instagram](https://www.instagram.com/enviraldesign/)
- [Discord](https://discord.gg/7rdfbgAPzK)

### Donations & Support
- [Patreon recuring](https://www.patreon.com/EnviralDesign)
- [GitHub recuring](https://github.com/sponsors/EnviralDesign)
- [PayPal one-time](https://www.paypal.com/donate?hosted_button_id=RP8EJAHSDTZ86)

## License

GeoPix is licensed under the permissive MIT license, TouchDesigner is [licensed differently](https://derivative.ca/end-user-license-agreement-eula).
