#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 11:49:57 2023

@author: ananya
"""
import pylab
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from pylab import sqrt
import os
import sys
import matplotlib.colors as colors

fig_width_pt = 500 # 300 #246.0 # Get this from LaTeX using \showthe\columnwidth
inches_per_pt = 1.0/72.27               # Convert pt to inch
golden_mean = (sqrt(5)+1.0)/2  # Aesthetic ratio =  1.618033988749895
fig_width =  fig_width_pt*inches_per_pt  # width in inches
# fig_height = 0.5*fig_width*golden_mean      # height in inches
# fig_height = 0.1*fig_width
# fig_height_pt = 0.1*fig_width_pt
# fig_size =  [fig_width,fig_height]
fig_size =  [fig_width,fig_width]
# t = np.linspace(0, 10, 200)
# x = np.cos(np.pi * t)
# y = np.sin(t)
# setting matplotlib rc parameters
params = {
          'backend': 'pdf',
          'axes.labelsize': 10,
          'font.size': 10,
          'legend.fontsize': 10,
          'xtick.labelsize': 10,
          'ytick.labelsize': 10,
          'text.usetex': True,
          'figure.figsize': fig_size,
          'font.family': 'DejaVu Sans',
          'axes.labelpad': 1,
          # 'axes.prop_cycle': cyc,
          # 'axes.edgecolor': 'w',
          'axes.formatter.use_mathtext': True,
          'axes.formatter.limits':(-10,10),
          # 'axes.labelcolor': 'w',
          'axes.spines.bottom': True,
          'axes.spines.left': True,
          'axes.spines.right': True,
          'axes.spines.top': True,
          # 'axes.titlecolor': 'w',
          # 'xtick.color':'w',
          # 'ytick.color':'w',
          # 'legend.labelcolor':'w',
          'legend.borderaxespad': 0.3,
          'legend.borderpad': 0.3,
          'legend.columnspacing': 0.5,
          'legend.handletextpad': 0.3,
          'legend.labelspacing': 0.3,
          'legend.framealpha':0,
          'lines.linewidth': 1, # 0.5,
          'lines.linestyle': '-',
          'lines.markeredgewidth': 1,
          'lines.markersize': 5, #10,
          'markers.fillstyle': 'none',
          'grid.linestyle':'-',
          # 'grid.linewidth':0.75,
          'grid.alpha':0.4,
         }
pylab.rcParams.update(params)


# f = '/home/ananya/research/DNS/GW190425_MPA1/post_proc/MPA1_q1_192/moving_puncture_distance.lxyz6'
# path = '/home/ananya/research/NS_EFL/BAM_113/moving_puncture_distance.lxyz8'
# f = sys.argv[1]
path = sys.argv[1]
# d = np.loadtxt(f)

lines = None
if os.path.isfile(path): # if file exists
    
    f = open(path,"r")
    lines = f.readlines()[1:]
    f.close()
    
if lines:

  d = np.loadtxt(lines)
    
  x1 = d[:,0]  
  y1 = d[:,1]
  # colors = np.sqrt(y11*y1 + x1*x1)
  t =  d[:,8] # np.sqrt(y1*y1 + x1*x1)
  # plt.figure(facecolor='#1a1a18')
  # plt.scatter(x,y,c=colors, cmap='copper')
  # Create a set of line segments so that we can color them individually
  # This creates the points as a N x 1 x 2 array so that we can stack points
  # together easily to get the segments. The segments array for line collection
  # needs to be numlines x points per line x 2 (x and y)
  points1 = np.array([x1, y1]).T.reshape(-1, 1, 2)
  segments1 = np.concatenate([points1[:-1], points1[1:]], axis=1)
  
  # cmap = plt.get_cmap('Oranges')
  cmap = plt.get_cmap('winter')#.reversed()
  new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name,a=0.1,b=0.9),
        cmap(np.linspace(0.1,0.9,200)))
  # Create the line collection object, setting the colormapping parameters.
  # Have to set the actual values used for colormapping separately.
  lc1 = LineCollection(segments1, cmap=new_cmap, #plt.get_cmap('Wistia'),
      norm=plt.Normalize(t.min(), t.max()))
  lc1.set_array(t)
  lc1.set_linewidth(2)
  
  plt.gca().add_collection(lc1)
  
  if not '-p1' in sys.argv:
  
    x2 = d[:,3]
    y2 = d[:,4]
    # colors = np.sqrt(y11*y1 + x1*x1)
    # r2 =  np.sqrt(y2*y2 + x2*x2)
    
    # plt.scatter(x,y,c=colors, cmap='copper')
    # Create a set of line segments so that we can color them individually
    # This creates the points as a N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line collection
    # needs to be numlines x points per line x 2 (x and y)
    points2 = np.array([x2, y2]).T.reshape(-1, 1, 2)
    segments2 = np.concatenate([points2[:-1], points2[1:]], axis=1)
    
    cmap = plt.get_cmap('autumn').reversed()
    new_cmap = colors.LinearSegmentedColormap.from_list(
          'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name,a=0.3,b=1.0),
          cmap(np.linspace(0.3,1.0,200)))
    
    # Create the line collection object, setting the colormapping parameters.
    # Have to set the actual values used for colormapping separately.
    lc2 = LineCollection(segments2, cmap=new_cmap,#cool'),
        norm=plt.Normalize(t.min(), t.max()))
    lc2.set_array(t)
    lc2.set_linewidth(2)
    
    plt.gca().add_collection(lc2)
    
    xmin = np.array([x1.min(),x2.min()]).min()
    xmin = xmin - 0.05*np.abs(xmin)
    xmax = np.array([x1.max(),x2.max()]).max()
    xmax = xmax + 0.05*xmax
    
    ymin = np.array([y1.min(),y2.min()]).min()
    ymin = ymin - 0.05*np.abs(ymin)
    ymax = np.array([y1.max(),y2.max()]).max()
    ymax = ymax + 0.05*ymax
    
  else:
    
    xmin = x1.min()
    xmin = xmin - 0.05*np.abs(xmin)
    xmax = x1.max()
    xmax = xmax + 0.05*xmax
    
    ymin = y1.min()
    ymin = ymin - 0.05*np.abs(ymin)
    ymax = y1.max()
    ymax = ymax + 0.05*ymax
  
  plt.xlim(xmin,xmax)
  plt.ylim(ymin,ymax)
  
  # plt.gca().set_facecolor("#303030")
  # plt.gca().set_facecolor("#1a1a18")
  plt.gca().set_aspect('equal')
  # plt.show()
  
  # name = f+'.orb.pdf'
  name = path+'.orb.pdf'
  plt.savefig(name)
  os.system("pdfcrop " + name +" " + name)