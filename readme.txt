How to use PyNPGS to assist design file preparation for the Nabity e-beam system

Setting up the design file
1) Create a GDS file in the design software of your choice.
1a) Make sure alignment marks are each in a separate layer (I use 11-14 for the four corners)
2) Drag this into C:\NPGS\Projects
3) Open NPGS Menu, convert to DC2 with DesignCAD Drawing Unit Size = 1.0 (leave all other parameters at their default values; you can change the filename if you wish)
4) Open the created .dc2 file in DesignCAD through NPGS Menu
5) Save to the NPGS Project via NPGS > Save
6) Run the dc2 file through make_align to convert alignment marks to solid and add windows around alignment marks
    Edited file is (your_old_file_name)_align.dc2
7) Open the dc2 file with NPGS
8) Set dump point (click a spot away from your pattern, then click a few more times to accept the rest of the options)
8a) Double click dump point and change layer to the layer of your first alignment mark. Dump point cannot be in a layer by itself.
9) Fix origin of pattern using NPGS > MaxMag. It may suggest to shift the origin to increase the maximum magnification. It's always a good idea to do this.
10) Change exposure order using NPGS > Order Entities.
11) NPGS > Save

Creating a run file
1) Right click design file ... Run File Editor
2) Select the first entity block
3) Copy Entity, Paste Entity
4) Change first entity type to Alignment (second should stay at Pattern)
5) Save run file
6) Pass the RF6 runfile to setup_run_file to configure alignment marks and exposure information
7) Simulate writing the runfile to make sure everything looks okay.
8) Once at the tool, make sure to set configuration parameter (aperture) and beam current
9) Expose!
