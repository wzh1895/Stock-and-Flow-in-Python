# Stock and Flow Canvas

## Introduction

This is a python realization of Stock and Flow Diagram display, based on **Tkinter**.
The intention is to allow users to visually view the model.
Here you can have a quick glance of it:

**Model display:**

![ScreenShot](./screenShots/screenShot_02.png)

**Simulation result display:**

![ScreenShot](./screenShots/screenShot_04.png)

## How to use

**Local-based**

Stock and flow diagrams created by Stella can be displayed using this software.

To display the diagram itself, no additional package other than **Python3** is needed.

To simulate the the model and display the result, **PySD** and **matplotlib** are also needed.

The program could be run from terminal, powershell, or CMD by executing:

```
python3 localMain.py
```

Then you can load the model, simulate and view the outcome in the graphic interface.

**Web-based (Still Trying)**

To deploy the program as a web application, you need **FlexxUI** and **Tornado**.

On linux or macOS, execute:

```
python3 webMain.py --flexx-hostname=0.0.0.0 --flexx-port=8080
```

The line above may be different from the FlexxUI document, but it was proven to be working well.

## Acknowledgement

Many thanks given to the **PySD** project.

The web application is made possible with **FlexxUI** project.

## Change Log

**15 Dec 2018: v0.3.1**

1.  Canvas in HTML5 is used to draw a first stock.

**23 Nov 2018: v0.3.0**

1.  Starting dev of webApp based on FlexxUI

**22 Nov 2018: v0.2.3**

1.  Able to draw bended flows.

**19 Nov 2018: v0.2.2**

1.  Canvas scrolling feature added.

**18 Nov 2018: v0.2.1**

1.  Able to select variable.
2.  Show result in a standalone window.

**17 Nov 2018: v0.2.0**

1.  Initial interface to PySD. Now able to run the model.
2.  Incorporated graph display using matplotlib to display simulation result of one variable. (Still testing, now only work with reindeerModel.stmx)

**15 Nov 2018: v0.1.1**

1.  Connector display function rewritten. Now connectors could be displayed in almost the identical way Stella is using.
2.  GUI-based model loading function added.

**10 Nov 2018: v0.1.0**
1.  First Commit.
