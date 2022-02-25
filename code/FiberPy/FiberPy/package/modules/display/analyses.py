# -*- coding: utf-8 -*-
"""
Created on Wed May 19 16:30:00 2021

@author: kscamp3
"""

import os

import numpy as np
import pandas as pd

from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from natsort import natsorted

from package.modules.analysis import curve_fitting as cv
from package.modules.utilities import utilities as ut

def default_formatting():
    formatting = dict()
    formatting['data_linewidth'] = 1
    formatting['fontname'] = 'Arial'
    formatting['marker_size'] = 8
    formatting['marker_symbols'] = ['o','s','^','v']
    formatting['high_pCa_tick'] = 8.0
    formatting['high_pCa_span'] = 0.2
    formatting['low_pCa_ticks'] = [6.5, 5.5, 4.5]
    formatting['low_pCa_pad'] = 0.2
    formatting['x_label_fontsize'] = 12
    formatting['x_label_pad'] = 15
    formatting['tick_labels_fontsize'] = 12
    formatting['x_scaling_factor'] = 1
    formatting['y_scaling_factor'] = 1
    formatting['x_normalized_to_max'] = False
    formatting['y_normalized_to_max'] = False
    formatting['x_field'] = 'pCa'
    formatting['x_axis_label'] = 'x_axis_label'
    formatting['y_axis_label'] = 'y_axis_label'
    formatting['y_label_pad'] = 15
    formatting['y_label_fontsize'] = 12
    formatting['y_label_rotation'] = 0
    formatting['table_y_anchor'] = 0.95
    formatting['table_y_spacing'] = 0.1
    formatting['table_x_spacing'] = 0.5
    formatting['table_fontsize'] = 11
    formatting['color_set'] = ["tab:orange", "tab:blue", "tab:green", "tab:red", "tab:pink", "tab:purple", "tab:grey", "tab:olive", "tab:cyan", "black"]
    formatting['labels'] = []

    return formatting


def create_y_pCa_figure(fig_data, batch_file_string):
    """ Creates a y pCa figure based on dict fig_data """

    # Pull default formatting, then overwrite any values from
    # input file
    formatting = default_formatting()
    if ('formatting' in fig_data):
        for entry in fig_data['formatting']:
            formatting[entry] = fig_data['formatting'][entry]

    # Iterate through the folder structure looking for curve data

    # Pull off the base folder
    base_folder = os.path.dirname(batch_file_string)

    # Set up current figure
    fig = plt.figure(constrained_layout=False)
    gs = fig.add_gridspec(nrows=1, ncols=6,
                          left=0.3, right=0.95, wspace=0.1,
                          bottom = 0.2)
    fig.set_size_inches([3.5, 2.5])
    ax_left = fig.add_subplot(gs[0,0])
    ax_right = fig.add_subplot(gs[0, 1:5])

    if (fig_data['relative_to'] == 'this_file'):
        top_data_folder = os.path.join(base_folder,
                                       fig_data['results_folder'])
    else:
        top_data_folder = fig_data['results_folder']

    # Store curve data in lists
    pCa_values = defaultdict(list)
    y_values = defaultdict(list)

    curve_counter = 1
    keep_going = True

    # Create lists to hold data
    curve_index = []
    hs_force = []
    hs_pCa = []
        
    # Keep track of max_y
    max_y = -np.inf
    
    # Set up a dictionary to store the curve data
    curve_data = dict()
    curve_data['curve'] = []

    while (keep_going):
        curve_folder = os.path.join(top_data_folder,
                                    ('%i' % curve_counter))
        if os.path.isdir(curve_folder):
            # Find the results files
            for file in os.listdir(curve_folder):
                if file.endswith('.txt'):
                    data_file_string = \
                        os.path.join(curve_folder, file)
                    d = pd.read_csv(data_file_string, delimiter='\t')
                    pCa_values[curve_counter-1].append(d['pCa'].iloc[-1])
                    y = formatting['y_scaling_factor'] * \
                            d[fig_data['data_field']].iloc[-1]
                    y_values[curve_counter-1].append(y)
                    if (np.amax(y) > max_y):
                        max_y = np.amax(y)
                    
                    # Store data for subsequent output
                    curve_index.append(curve_counter)
                    hs_force.append(y)
                    hs_pCa.append(d['pCa'].iloc[-1])

            # Add in curve
            res=cv.fit_pCa_data(pCa_values[curve_counter-1],
                                y_values[curve_counter-1])
            
            # Store data
            d_parameters = pd.DataFrame({'pCa_50': res['pCa_50'],
                                        'n_H': res['n_H'],
                                        'y_min': res['y_min'],
                                        'y_max': res['y_max']},
                                        index=[0])
            d_fits = pd.DataFrame({'x_fit': res['x_fit'],
                                    'y_fit': res['y_fit']});
            
            d_curve = pd.concat([d_parameters, d_fits])
            curve_data['curve'].append(d_curve)
            
            # plot

            # Normalized data_field if required
            if formatting['y_normalized_to_max']:
                res['y_fit'] = res['y_fit']/max(y_values[curve_counter-1])
                y_values[curve_counter-1] = [x/max(y_values[curve_counter-1]) for x in y_values[curve_counter-1]]                

            for a in [ax_left, ax_right]:
                a.plot(pCa_values[curve_counter-1],
                    y_values[curve_counter-1],
                    formatting['marker_symbols'][curve_counter-1],
                    markersize=formatting['marker_size'],
                    markerfacecolor = formatting['color_set'][curve_counter - 1],
                    markeredgewidth=0.0)
                if formatting['labels'] != []:
                    a.plot(res['x_fit'], res['y_fit'],'-',
                        color = formatting['color_set'][curve_counter - 1],
                        label = formatting['labels'][curve_counter - 1])

                a.plot(res['x_fit'], res['y_fit'],'-',
                    color = formatting['color_set'][curve_counter - 1])

            # Loop on to the next folder
            curve_counter = curve_counter + 1

        else:
            keep_going = False

    if formatting['labels'] != []:
        ax_right.legend(loc='upper left', bbox_to_anchor=[1.05, 1], fontsize = formatting['y_label_fontsize']-2)

    # Take lists and create a data frame
    r = pd.DataFrame({'curve': curve_index,
                      'hs_pCa': hs_pCa,
                      'hs_force': hs_force})

    # Tidy up axis
    ax_left.set_xlim(formatting['high_pCa_tick'] +
                     formatting['high_pCa_span']*np.asarray([0.5, -0.5]))
    right_lims = [formatting['low_pCa_ticks'][0] + formatting['low_pCa_pad'],
                  formatting['low_pCa_ticks'][-1]]
    ax_right.set_xlim(right_lims)

    ax_left.spines['right'].set_visible(False)
    ax_left.spines['top'].set_visible(False)
    ax_right.spines['left'].set_visible(False)
    ax_right.spines['right'].set_visible(False)
    ax_right.spines['top'].set_visible(False)
    ax_right.tick_params('y', left=False, labelleft=False)

    # Ticks
    ax_left.set_xticks([formatting['high_pCa_tick']])
    ax_left.set_ylabel(formatting['y_axis_label'],
                       loc='center',
                       verticalalignment='center',
                       labelpad=formatting['y_label_pad'],
                       fontfamily=formatting['fontname'],
                       fontsize=formatting['y_label_fontsize'],
                       rotation=formatting['y_label_rotation'])

    ax_right.set_xlabel('pCa',
                       loc='center',
                       verticalalignment='center',
                       labelpad=formatting['x_label_pad'],
                       fontfamily=formatting['fontname'],
                       fontsize=formatting['x_label_fontsize'])
    ax_right.set_xticks(formatting['low_pCa_ticks'])


    y_ticks = [0, ut.multiple_greater_than(max_y,
                                           0.05*np.power(10, np.ceil(np.log10(max_y))))]

    for a in [ax_left, ax_right]:
        a.set_xticklabels(a.get_xticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        a.set_ylim(y_ticks)
        a.set_yticks(y_ticks)
        a.set_yticklabels(a.get_yticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])

        if formatting['y_normalized_to_max']:
            y_ticks = [0,1]
            a.set_ylim([0,1.03])
            a.spines['left'].set_bounds(y_ticks)
            a.set_yticks(y_ticks)
            a.set_yticklabels(a.get_yticks(),
                fontsize=formatting['tick_labels_fontsize'],
                fontfamily=formatting['fontname'])

    # Draw split
    # proportion of vertical to horizontal extent of the slanted line
    d = 0.5
    kwargs = dict(marker=[(-d, -1), (d, 1)],
                  linestyle='none',
                  markersize=10,
                  mec='k', mew=1,
                  color='k', clip_on=False)
    ax_left.plot([1], [0], transform=ax_left.transAxes, **kwargs)
    ax_right.plot([0], [0], transform=ax_right.transAxes, **kwargs)

    # Draw table
    y_anchor = formatting['table_y_anchor'] * y_ticks[-1]
    y_spacing = formatting['table_y_spacing'] * y_ticks[-1]
    x_anchor = formatting['low_pCa_ticks'][0]

    ax_right.text(x_anchor,
                 y_anchor,
                 'pCa$\\mathregular{_{50}}$',
                 fontfamily=formatting['fontname'],
                 fontsize=formatting['table_fontsize'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 clip_on=False)
    ax_right.text(x_anchor - 1 * formatting['table_x_spacing'],
                 y_anchor,
                 'n$\\mathregular{_{H}}$',
                 fontfamily=formatting['fontname'],
                 fontsize=formatting['table_fontsize'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 clip_on=False)
    
    # Add in data
    for i,c in enumerate(curve_data['curve']):
        y_anchor = y_anchor - y_spacing
        ax_right.plot(x_anchor + formatting['table_x_spacing'],
                    y_anchor,
                    formatting['marker_symbols'][i],
                    mfc = formatting['color_set'][i],
                    mec = formatting['color_set'][i],
                    markersize=formatting['marker_size'],
                    clip_on=False)

        ax_right.text(x_anchor,
                    y_anchor,
                    '%.2f' % c['pCa_50'].iloc[0],
                    fontfamily=formatting['fontname'],
                    fontsize=formatting['table_fontsize'],
                    horizontalalignment='center',
                    verticalalignment='center',
                    clip_on=False)
        ax_right.text(x_anchor - formatting['table_x_spacing'],
                    y_anchor,
                    '%.2f' % c['n_H'].iloc[0],
                    fontfamily=formatting['fontname'],
                    fontsize=formatting['table_fontsize'],
                    horizontalalignment='center',
                    verticalalignment='center',
                    clip_on=False)

    # Save the figure
    if ('output_image_file' in fig_data):
        if (fig_data['relative_to'] == 'this_file'):
                fig_data['output_image_file'] = \
                    os.path.join(base_folder,
                                 fig_data['output_image_file'])

        # Check dir exists
        dir_name = os.path.dirname(fig_data['output_image_file'])
        if (not os.path.isdir(dir_name)):
            os.makedirs(dir_name)
            
        for f in fig_data['output_image_formats']:
            ofs = '%s.%s' % (fig_data['output_image_file'], f)
            print('Saving pCa_figure to: %s' % ofs)
            fig.savefig(ofs, dpi=200, bbox_inches='tight')
            
    plt.close()

    # Save the data as an excel file if required in the batch file
    if(fig_data['output_data_file_string']):
        if (fig_data['relative_to'] == 'this_file'):
            output_file_string = os.path.join(base_folder,
                                              fig_data['output_data_file_string'])
        else:
            output_file_string = fig_data['output_data_file_string']

        print('Writing tension-pCa data to %s' % output_file_string)
        with pd.ExcelWriter(output_file_string, engine='openpyxl') as writer:
            r.to_excel(writer, sheet_name = 'simulation_data', index=False)
            for (i,c) in enumerate(curve_data['curve']):
                c.to_excel(writer,
                           index=False,
                           sheet_name = 'curve_%i' % (i+1))


def create_fv_and_power_figure(fig_data, batch_file_string):
    """ Creates an fv and power figure """
    
    print("fig_data")
    print(fig_data)
    print(batch_file_string)

    # Pull default formatting, then overwrite any values from
    # input file
    formatting = default_formatting()
    if ('formatting' in fig_data):
        for entry in fig_data['formatting']:
            formatting[entry] = fig_data['formatting'][entry]

    # Find the data folders
    base_folder = os.path.dirname(batch_file_string)

    if (fig_data['relative_to'] == 'this_file'):
        top_data_folder = os.path.join(base_folder,
                                       fig_data['results_folder'])
    else:
        top_data_folder = fig_data['results_folder']

    curve_counter = 1
    keep_going = True

    # Create lists to hold data
    curve = []
    hs_force = []
    hs_velocity = []
    hs_rel_velocity = []
    hs_power = []

    while keep_going:
        curve_folder = os.path.join(top_data_folder,
                                    ('%i' % curve_counter))
        if (os.path.isdir(curve_folder)):
            # Find the results files
            for file in os.listdir(curve_folder):
                if file.endswith('.txt'):
                    data_file_string = os.path.join(curve_folder, file)
                    print('dfs %s' % data_file_string)

                    # Load up the results file
                    d = pd.read_csv(data_file_string, delimiter='\t')
                    initial_hsl = d['hs_length'].iloc[0]

                    # Filter to fit time_interval
                    d_fit = d.loc[(d['time'] >= fig_data['fit_time_interval_s'][0]) &
                                  (d['time'] <= fig_data['fit_time_interval_s'][-1])]

                    vel_data = cv.fit_straight_line(d_fit['time'].to_numpy(),
                                                    d_fit['hs_length'].to_numpy())
              
                    # Calculate some values, with a -ve for shortening velocity
                    hs_vel = -1e-9*vel_data['slope']
                    hs_rel_vel = 1e9 * hs_vel / initial_hsl
                    hs_for = d_fit['force'].mean()
                    hs_pow = hs_vel * hs_for / (1e-9 * initial_hsl)

                    # Store data
                    curve.append(curve_counter)
                    hs_velocity.append(hs_vel)
                    hs_rel_velocity.append(hs_rel_vel)
                    hs_force.append(hs_for)
                    hs_power.append(hs_pow)

            curve_counter = curve_counter + 1

        else:
            keep_going = False

    # Take lists and create a data frame
    r = pd.DataFrame({'curve': curve,
                      'hs_velocity': hs_velocity,
                      'hs_rel_velocity': hs_rel_velocity,
                      'hs_force': hs_force,
                      'hs_power': hs_power})

    # Create a figure
    if ('output_image_file' in fig_data):

        # Make a figure
        fig = plt.figure(constrained_layout=True)
        gs = fig.add_gridspec(nrows=2, ncols=2,
                              wspace = 0.5,
                              hspace=0.1)
        fig.set_size_inches([7, 5])
        ax_fv = fig.add_subplot(gs[0,0])
        ax_pow = fig.add_subplot(gs[1, 0])
        ax_rel_fv = fig.add_subplot(gs[0,1])
        ax_rel_pow = fig.add_subplot(gs[1,1])

        # Hold ticks
        f_ticks = np.asarray([])
        rel_f_ticks = np.asarray([])
        v_ticks = np.asarray([])
        rel_v_ticks = np.asarray([])
        p_ticks = np.asarray([])
        rel_p_ticks = np.asarray([])
        
        # Set up dict to store the curve data
        curve_data = dict()
        curve_data['curve'] = []
        
        # Cycle through curves
        for c in range(1, curve_counter):
            # Pull off the curve data
            rc = r[r['curve'] == c].copy()
            
            # Normalize force
            rc['hs_rel_force'] = rc['hs_force'] / rc['hs_force'].max()
            rc['hs_rel_power'] = rc['hs_rel_force'] * rc['hs_rel_velocity']

            # Plot the force velocity curve
            ax_fv.plot(rc['hs_force'], rc['hs_velocity'], 'o',
                       color = formatting['color_set'][c - 1])
            fv_curve = cv.fit_hyperbola(rc['hs_force'], rc['hs_velocity'])
            ax_fv.plot(fv_curve['x_fit'], fv_curve['y_fit'], '-',
                       color=ax_fv.lines[-1].get_color())

            ax_pow.plot(rc['hs_force'], rc['hs_power'], 'o',
                        color = formatting['color_set'][c - 1])
            pow_curve = cv.fit_power_curve(rc['hs_force'], rc['hs_power'])
            ax_pow.plot(pow_curve['x_fit'], pow_curve['y_fit'], '-',
                        color=ax_pow.lines[-1].get_color())

            ax_rel_fv.plot(rc['hs_rel_force'], rc['hs_rel_velocity'], 'o',
                           color = formatting['color_set'][c-1])
            rel_fv_curve = cv.fit_hyperbola(rc['hs_rel_force'], rc['hs_rel_velocity'])
            ax_rel_fv.plot(rel_fv_curve['x_fit'], rel_fv_curve['y_fit'], '-',
                           color=ax_rel_fv.lines[-1].get_color())

            ax_rel_pow.plot(rc['hs_rel_force'], rc['hs_rel_power'], 'o',
                        color = formatting['color_set'][c - 1])
            rel_pow_curve = cv.fit_power_curve(rc['hs_rel_force'], rc['hs_rel_power'])
            ax_rel_pow.plot(rel_pow_curve['x_fit'], rel_pow_curve['y_fit'], '-',
                        color=ax_pow.lines[-1].get_color())

            # Store data to work out ticks later on
            f_ticks = np.concatenate((f_ticks, rc['hs_force']))
            rel_f_ticks = np.concatenate((rel_f_ticks, rc['hs_rel_force']))
            v_ticks = np.concatenate((v_ticks, rc['hs_velocity']))
            rel_v_ticks = np.concatenate((rel_v_ticks, rc['hs_rel_velocity']))
            p_ticks = np.concatenate((p_ticks, rc['hs_power']))
            rel_p_ticks = np.concatenate((rel_p_ticks, rc['hs_rel_power']))
            
            # Store the curve data
            d_parameters = pd.DataFrame({'fv_x_0': fv_curve['x_0'],
                                         'fv_a': fv_curve['a'],
                                         'fv_b': fv_curve['b'],
                                         'pow_x_0': pow_curve['x_0'],
                                         'pow_a': pow_curve['a'],
                                         'pow_b': pow_curve['b'],
                                         'rel_fv_x_0': rel_fv_curve['x_0'],
                                         'rel_fv_a': rel_fv_curve['a'],
                                         'rel_fv_b': rel_fv_curve['b'],
                                         'rel_pow_x_0': rel_pow_curve['x_0'],
                                         'rel_pow_a': rel_pow_curve['a'],
                                         'rel_pow_b': rel_pow_curve['b']},
                                        index=[0])
            d_fits = pd.DataFrame({'fv_x_fit': fv_curve['x_fit'],
                                   'fv_y_fit': fv_curve['y_fit'],
                                   'pow_x_fit': pow_curve['x_fit'],
                                   'pow_y_fit': pow_curve['y_fit'],
                                   'rel_fv_x_fit': rel_fv_curve['x_fit'],
                                   'rel_fv_y_fit': rel_fv_curve['y_fit'],
                                   'rel_pow_x_fit': rel_pow_curve['x_fit'],
                                   'rel_pow_y_fit': rel_pow_curve['y_fit']})
            d_curve = pd.concat([d_parameters, d_fits])
            curve_data['curve'].append(d_curve)

        # Tidy up
            
        # Shortening velocity against stress
        xt = ut.tidy_limits(f_ticks)
        ax_fv.set_xlim(xt)
        ax_fv.set_xticks(xt)
        ax_fv.set_xticklabels(ax_fv.get_xticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        yt = ut.tidy_limits(v_ticks)
        ax_fv.set_ylim(yt)
        ax_fv.set_yticks(yt)
        ax_fv.set_yticklabels(ax_fv.get_yticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        ax_fv.set_xlabel('Force (N m$^{\\mathregular{-2}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center')
        ax_fv.set_ylabel('Shortening\nvelocity\n(m s$^{\\mathregular{-1}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center',
                          verticalalignment='center',
                          rotation=formatting['y_label_rotation'])

        # Power in W m^-3 against Stress
        ax_pow.set_xlim(xt)
        ax_pow.set_xticks(xt)
        ax_pow.set_xticklabels(ax_pow.get_xticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        yt = ut.tidy_limits(p_ticks)
        ax_pow.set_ylim(yt)
        ax_pow.set_yticks(yt)
        ax_pow.set_yticklabels(ax_pow.get_yticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        ax_pow.set_xlabel('Force (N m$^{\\mathregular{-2}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center')
        ax_pow.set_ylabel('Power\n(W m$^{\\mathregular{-3}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center',
                          verticalalignment='center',
                          rotation=formatting['y_label_rotation'])
        
        # Rel velocity against rel force
        xt = ut.tidy_limits(rel_f_ticks)
        ax_rel_fv.set_xlim(xt)
        ax_rel_fv.set_xticks(xt)
        ax_rel_fv.set_xticklabels(ax_rel_fv.get_xticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        yt = ut.tidy_limits(rel_v_ticks)
        ax_rel_fv.set_ylim(yt)
        ax_rel_fv.set_yticks(yt)
        ax_rel_fv.set_yticklabels(ax_rel_fv.get_yticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        ax_rel_fv.set_xlabel('Relative force',
                          fontfamily=formatting['fontname'],
                          loc='center')
        ax_rel_fv.set_ylabel('Relative\nshortening\nvelocity\n(l$_{\\mathregular{0}}$ s$^{\\mathregular{-1}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center',
                          verticalalignment='center',
                          rotation=formatting['y_label_rotation'])

        # Rel power against rel force
        xt = ut.tidy_limits(rel_f_ticks)
        ax_rel_pow.set_xlim(xt)
        ax_rel_pow.set_xticks(xt)
        ax_rel_pow.set_xticklabels(ax_rel_fv.get_xticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        yt = ut.tidy_limits(rel_p_ticks)
        ax_rel_pow.set_ylim(yt)
        ax_rel_pow.set_yticks(yt)
        ax_rel_pow.set_yticklabels(ax_rel_fv.get_yticks(),
                          fontsize=formatting['tick_labels_fontsize'],
                          fontfamily=formatting['fontname'])
        ax_rel_pow.set_xlabel('Relative force',
                          fontfamily=formatting['fontname'],
                          loc='center')
        ax_rel_pow.set_ylabel('Relative\npower',
                          fontfamily=formatting['fontname'],
                          loc='center',
                          verticalalignment='center',
                          rotation=formatting['y_label_rotation'])

    # Save the figure
    if ('output_image_file' in fig_data):
        if (fig_data['relative_to'] == 'this_file'):
                fig_data['output_image_file'] = \
                    os.path.join(base_folder,
                                 fig_data['output_image_file'])

        # Check dir exists
        dir_name = os.path.dirname(fig_data['output_image_file'])
        if (not os.path.isdir(dir_name)):
            os.makedirs(dir_name)
            
        for f in fig_data['output_image_formats']:
            ofs = '%s.%s' % (fig_data['output_image_file'], f)
            print('Saving pCa_figure to: %s' % ofs)
            fig.savefig(ofs, dpi=200, bbox_inches='tight')
            
    plt.close()
        
    # Save the data as an excel file
    if ('output_data_file_string' in fig_data):
        if (fig_data['relative_to'] == 'this_file'):
            output_file_string = os.path.join(base_folder,
                                              fig_data['output_data_file_string'])
        else:
            output_file_string = fig_data['output_data_file_string']
    
        with pd.ExcelWriter(output_file_string, engine='openpyxl') as writer:
            r.to_excel(writer, sheet_name = 'simulation_data', index=False)
            for (i,c) in enumerate(curve_data['curve']):
                c.to_excel(writer,
                       index=False,
                       sheet_name = ('curve_%i' % (i+1)))


def create_ktr_figure(fig_data, batch_file_string):
    """ Creates ktr figure based on dict fig_data """

    # Pull default formatting, then overwrite any values from
    # input file
    formatting = default_formatting()
    if ('formatting' in fig_data):
        for entry in fig_data['formatting']:
            formatting[entry] = fig_data['formatting'][entry]

    # Iterate through the folder structure looking for curve data

    # Pull off the base folder
    base_folder = os.path.dirname(batch_file_string)

    if (fig_data['relative_to'] == 'this_file'):
        top_data_folder = os.path.join(base_folder,
                                       fig_data['results_folder'])
    else:
        top_data_folder = fig_data['results_folder']

    curve_counter = 1
    keep_going = True

    # Create lists to hold data
    curve = []
    hs_ktr = []
    hs_pCa = []
    hs_force = []

    while keep_going:
        curve_folder = os.path.join(top_data_folder,
                                    ('%i' % curve_counter))
        if (os.path.isdir(curve_folder)):
            # Find the results files
            for file in os.listdir(curve_folder):
                if file.endswith('.txt'):
                    data_file_string = os.path.join(curve_folder, file)

                    # Load up the results file
                    d = pd.read_csv(data_file_string, delimiter='\t')

                    # Filter to fit time_interval
                    d_fit = d.loc[(d['time'] >= fig_data['fit_time_interval_s'][0]) &
                                  (d['time'] <= fig_data['fit_time_interval_s'][-1])]

                    
                    # Set the time origin to 0
                    orig_time = d_fit['time'] - fig_data['fit_time_interval_s'][0]

                    ktr_data = cv.fit_exponential_recovery(orig_time.to_numpy(),
                                                    d_fit['force'].to_numpy())
                    
                    # Store data
                    curve.append(curve_counter)
                    hs_ktr.append(ktr_data['k'])
                    hs_pCa.append(d_fit['pCa'].iloc[-1])
                    hs_force.append(formatting['x_scaling_factor'] * d_fit['force'].iloc[-1])

            curve_counter = curve_counter + 1

        else:
            keep_going = False

    # Take lists and create a data frame
    r = pd.DataFrame({'curve': curve,
                    'hs_pCa': hs_pCa,
                    'hs_force': hs_force,
                    'hs_ktr': hs_ktr})

    # Create a figure
    if ('output_image_file_string' in fig_data):
        # Deduce the output file string
        if (fig_data['relative_to'] == 'this_file'):
            output_image_file_string = os.path.join(
                base_folder, fig_data['output_image_file_string'])
        else:
            output_image_file_string = fig_data['output_image_file_string']

        # Make a figure
        fig = plt.figure(constrained_layout=True)
        gs = fig.add_gridspec(nrows=1, ncols=1,
                              wspace = 0.5,
                              hspace=0.1)
        fig.set_size_inches([7, 3.5])
        ax_ktr = fig.add_subplot(gs[0,0])

        # Cycle through curves
        for c in range(1, curve_counter):
            rc = r[r['curve'] == c]

            if formatting['x_field']== "force": # plot ktr-force curve

                # Normalized data_field if required
                if formatting['x_normalized_to_max']:
                    rc['hs_force'] = rc['hs_force']/max(rc['hs_force'])

                # Plot the ktr curve
                ax_ktr.plot(rc['hs_force'], rc['hs_ktr'], '--o', color = formatting['color_set'][c - 1])

                ax_ktr.set_xlabel(formatting['x_axis_label'],
                        fontfamily=formatting['fontname'],
                        loc='center')

                ax_ktr.set_ylabel('k$_{\\mathregular{tr}}$\n(s$^{\\mathregular{-1}}$)',
                          fontfamily=formatting['fontname'],
                          loc='center',
                          rotation=formatting['y_label_rotation'])


            if formatting['x_field'] == "pCa": # plot ktr-pCa curve 

                # Plot the ktr curve
                ax_ktr.plot(rc['hs_pCa'], rc['hs_ktr'], '--o', color = formatting['color_set'][c - 1])
                
                ax_ktr.set_xlabel('pCa',
                                    fontfamily=formatting['fontname'],
                                    loc='center')
                ax_ktr.set_ylabel('k$_{\\mathregular{tr}}$\n(s$^{\\mathregular{-1}}$)',
                                    fontfamily=formatting['fontname'],
                                    loc='center',
                                    rotation=formatting['y_label_rotation'])

                ax_ktr.invert_xaxis()

        # Save figure
        print('Saving ktr figure to: %s'% output_image_file_string)
        dir_name = os.path.dirname(output_image_file_string)
        if (not os.path.isdir(dir_name)):
            os.makedirs(dir_name)
        fig.savefig(output_image_file_string)
        plt.close()

    # Save the data as an excel file
    if (fig_data['relative_to'] == 'this_file'):
        output_file_string = os.path.join(base_folder,
                                          fig_data['output_data_file_string'])
    else:
        output_file_string = fig_data['output_data_file_string']
    print('Writing k_tr data to %s' % output_file_string)
    r.to_excel(output_file_string,
               engine='openpyxl',
               index=False)

def superpose_ktr_plots(fig_data, batch_file_string):
    """ Superpose k_tr data from multiple result files """

    # Pull default formatting, then overwrite any values from
    # input file
    formatting = default_formatting()
    if ('formatting' in fig_data):
        for entry in fig_data['formatting']:
            formatting[entry] = fig_data['formatting'][entry]

    # Pull off the base folder
    base_folder = os.path.dirname(batch_file_string)

    if (fig_data['relative_to'] == 'this_file'):
        top_data_folder = os.path.join(base_folder,
                                       fig_data['results_folder'])
    else:
        top_data_folder = fig_data['results_folder']

    # Pull data
    # Loop through the txt files in top_data_folder
    # add to a list, then naturally sort the list

    results_files = []

    for file in os.listdir(top_data_folder): # iterate over all files in results_folder
        if file.endswith('.txt'): # this is a results file
            file = os.path.join(top_data_folder, file)
            results_files.append(file)

    results_files = natsorted(results_files) 

    # Create figure

    if ('output_image_file_string' in fig_data):
        # Deduce the output file string
        if (fig_data['relative_to'] == 'this_file'):
            output_image_file_string = os.path.join(
                base_folder, fig_data['output_image_file_string'])
        else:
            output_image_file_string = fig_data['output_image_file_string']

    fig = plt.figure(constrained_layout=False)
    fig.set_size_inches([3.5, 7])
    spec = gridspec.GridSpec(nrows=5, ncols=1, figure=fig,
                             wspace=1)
    axs=[]
    for r in range(0,5):
        axs.append(fig.add_subplot(spec[r,0]))

    # Plot data

    for i in range(0, len(results_files)):

        d = pd.read_csv(results_files[i], sep='\t')
        x = d['time']

        # Set max time on x axis

        max_time = ut.multiple_greater_than(max(d["time"]),
            0.05*np.power(10, np.ceil(np.log10(max(d["time"])))))

        # pCa

        axs[0].plot(x, d['pCa'], color = formatting['color_set'][i])

        # HSL length + command

        axs[1].plot(x, d['hs_length'], color = "black")
        axs[1].plot(x, d['hs_command_length'], color = "tab:orange", linestyle='--')

        if i == len(results_files) -1:
            axs[1].plot(x, d['hs_length'], color = "black", label = "Length")
            axs[1].plot(x, d['hs_command_length'], color = "tab:red", linestyle='--', label = "Length \ncommand")
            axs[1].legend(loc='upper left', bbox_to_anchor=[0.55, 0.9], fontsize = 12, handlelength=1.0)        

        # Force

        d['force'] = d['force']/1000

        if formatting['labels'] != []:        
            axs[2].plot(x, d['force'], label = formatting['labels'][i], color = formatting['color_set'][i], zorder=len(results_files) - i)

        else:
            axs[2].plot(x, d['force'], color = formatting['color_set'][i], zorder=len(results_files) - i)

        if formatting['labels'] != []:
            axs[2].legend(loc='upper left', bbox_to_anchor=[0.65, 0.65], fontsize = 11)

        # Actin pop
        axs[3].plot(x, d['a_pop_0'], '--' , color = formatting['color_set'][i], zorder=len(results_files) - i)
        axs[3].plot(x, d['a_pop_1'], '-' , color = formatting['color_set'][i], zorder=len(results_files) - i)

        # Myosin pop
        axs[4].plot(x, d['m_pop_0'], '--' , color = formatting['color_set'][i], zorder=len(results_files) - i)
        axs[4].plot(x, d['m_pop_1'], '-' , color = formatting['color_set'][i], zorder=len(results_files) - i)
        axs[4].plot(x, d['m_pop_2'], '-' , color = formatting['color_set'][i], zorder=len(results_files) - i)

    # Clean axis

    for i in range(5):
        
        axs[i].spines['top'].set_visible(False)
        axs[i].spines['right'].set_visible(False)
        axs[i].spines['bottom'].set_visible(False)
        axs[i].set_xticks([])
        axs[i].set_xlim([0, max_time]) 
        
        for axis in ['top','bottom','left','right']:
            axs[i].spines[axis].set_linewidth(1.5)
            
        for tick in axs[i].yaxis.get_major_ticks():
            tick.label.set_fontsize(14) 
            
        axs[i].tick_params(direction = "out", length = 6, width = 1.5)

    axs[4].spines['bottom'].set_visible(True)

    axs[4].set_xlim([0, max_time]) 
    axs[4].set_xticks([0, max_time])
    axs[4].set_xlabel('Time (s)', labelpad = -5)
    
    # Y lables and axis limits

    axs[0].set_ylim([9, 4])
    axs[0].set_yticks([9, 4])
    axs[0].text(-0.2, 6.5, "pCa" , fontsize = 14, transform = axs[0].transData, ha='center', va='center')

    max_length =ut. multiple_greater_than(max(d["hs_command_length"]),
               0.001*np.power(10, np.ceil(np.log10(max(d["hs_command_length"])))))

    min_length = ut.multiple_greater_than(min(d["hs_command_length"]),
               0.001*np.power(10, np.ceil(np.log10(min(d["hs_command_length"])))))

    axs[1].set_ylim([min_length-0.5, max_length+0.5])
    axs[1].set_yticks([min_length, max_length])

    axs[1].text(-0.2, (max_length + min_length)/2, "HS length \n($\mathregular{\mu}$m)" , fontsize = 14, transform = axs[1].transData, ha='center', va='center')

    max_force = ut.multiple_greater_than(max(d["force"]),
               0.1*np.power(10, np.ceil(np.log10(max(d["force"])))))

    axs[2].set_ylim([0, max_force])
    axs[2].set_yticks([0, max_force])

    axs[2].text(-0.2, (0 + max_force)/2, 'Force \n(kN $\\mathregular{m}^{\mathregular{-2}}$)' , fontsize = 14, transform = axs[2].transData, ha='center', va='center')

    axs[3].text(-0.2, 0.5, 'Thin \n filament' , fontsize = 14, transform = axs[3].transData, ha='center', va='center')

    axs[3].set_ylim([0, 1])
    axs[3].set_yticks([0, 1])

    axs[4].text(-0.2, 0.5, 'Thick \n filament' , fontsize = 14, transform = axs[4].transData, ha='center', va='center')
    axs[4].set_ylim([0, 1])
    axs[4].set_yticks([0, 1])

    # Save figure
    print('Saving superposing plot figure to %s' % output_image_file_string)
    # Check folder exists and make it if not
    dir_name = os.path.dirname(os.path.abspath(
        output_image_file_string))
    if (not os.path.isdir(dir_name)):
            os.makedirs(dir_name)
    fig.savefig(output_image_file_string, bbox_inches='tight')
    plt.close()

def dose_response(fig_data, batch_file_string):
    """ Plot data as a function of myotrope dose """

    # Pull default formatting, then overwrite any values from
    # input file
    formatting = default_formatting()
    if ('formatting' in fig_data):
        for entry in fig_data['formatting']:
            formatting[entry] = fig_data['formatting'][entry]

    # Pull off the base folder
    base_folder = os.path.dirname(batch_file_string)

    if (fig_data['relative_to'] == 'this_file'):
        top_data_folder = os.path.join(base_folder,
                                       fig_data['results_folder'])
    else:
        top_data_folder = fig_data['results_folder']

    # Get the myotrope dose list

    dose = fig_data["dose_list"]
    drug_effect = fig_data["drug_effect"] # define if it is an increasing/decreasing Hill curve
    dose_counter = 0
    keep_going = True

   # Create lists to hold data
    curve = []
    y_values = []
    IC_50 = []
    n_H = []

    # Keep track of max_y
    max_y = -np.inf

     # Make a figure

    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(nrows=1, ncols=1)
    fig.set_size_inches([4, 3.5])
    ax = fig.add_subplot(gs[0,0])

    while keep_going:
        curve_folder = os.path.join(top_data_folder,
                                    ('%i' % dose_counter))
        if (os.path.isdir(curve_folder)):
            # Find the results files
            for file in os.listdir(curve_folder):
                if file.endswith('.txt'):

                    data_file_string = os.path.join(curve_folder, file)
                    d = pd.read_csv(data_file_string, delimiter='\t')

                    y = formatting['y_scaling_factor'] * \
                            d[fig_data['data_field']].iloc[-1]

                    if (np.amax(y) > max_y):
                        max_y = np.amax(y)

                    curve.append(dose_counter)
                    y_values.append(y)

            dose_counter = dose_counter + 1

        else:
            keep_going = False

    # Plot the dose response curve
    ax.plot(dose, y_values, formatting['marker_symbols'][0], markersize=formatting['marker_size'],
        markerfacecolor = formatting['color_set'][0],
        markeredgewidth=0.0)
    # Add fit
    res=cv.fit_IC_50(dose,y_values, drug_effect)

    # Store data
    IC_50.append(res['IC_50'])
    n_H.append(res['n_H']) 

    ax.plot(res['x_fit'], res['y_fit'], '-', color = formatting['color_set'][0])

    # Tidy up axis

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Log scale
    ax.set_xscale('log')

    # Ticks and labels

    ax.set_ylabel(formatting['y_axis_label'],
                       loc='center',
                       verticalalignment='center',
                       labelpad=formatting['y_label_pad'],
                       fontfamily=formatting['fontname'],
                       fontsize=formatting['y_label_fontsize'],
                       rotation=formatting['y_label_rotation'])

    ax.set_xlabel(formatting['x_axis_label'],
                       loc='center',
                       verticalalignment='center',
                       labelpad=formatting['x_label_pad'],
                       fontfamily=formatting['fontname'],
                       fontsize=formatting['x_label_fontsize'])


    y_ticks = [0, ut.multiple_greater_than(max_y,
                            0.1*np.power(10, np.ceil(np.log10(max_y))))]

    ax.set_ylim(y_ticks)
    ax.set_yticks(y_ticks)

    xticks = [0.01,0.1,1,10,100]
    ax.set_xticks(xticks)

    # Draw table
    y_anchor = formatting['table_y_anchor'] * y_ticks[-1]
    y_spacing = formatting['table_y_spacing'] * y_ticks[-1]
    x_anchor = xticks[-2]

    ax.text(x_anchor,
                 y_anchor,
                 'IC$\\mathregular{_{50}}$ ($\\mathregular{\mu}$M)',
                 fontfamily=formatting['fontname'],
                 fontsize=formatting['table_fontsize'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 clip_on=False)
    ax.text(x_anchor + 150 * formatting['table_x_spacing'],
                 y_anchor,
                 'n$\\mathregular{_{H}}$',
                 fontfamily=formatting['fontname'],
                 fontsize=formatting['table_fontsize'],
                 horizontalalignment='center',
                 verticalalignment='center',
                 clip_on=False)
    
    # Add in data
    for i in range(len(IC_50)):
        y_anchor = y_anchor - y_spacing
        ax.text(x_anchor,
                    y_anchor,
                    '%.2f' % IC_50[i],
                    fontfamily=formatting['fontname'],
                    fontsize=formatting['table_fontsize'],
                    horizontalalignment='center',
                    verticalalignment='center',
                    clip_on=False)
        ax.text(x_anchor + 150 * formatting['table_x_spacing'],
                    y_anchor,
                    '%.2f' % n_H[i],
                    fontfamily=formatting['fontname'],
                    fontsize=formatting['table_fontsize'],
                    horizontalalignment='center',
                    verticalalignment='center',
                    clip_on=False)

    # Take lists and create a data frame
    r = pd.DataFrame({'curve': curve,
                    'dose': dose,
                    fig_data['data_field']: y_values})

    # Save figure
    if ('output_image_file_string' in fig_data):
        # Deduce the output file string
        if (fig_data['relative_to'] == 'this_file'):
            output_image_file_string = os.path.join(
                base_folder, fig_data['output_image_file_string'])
        else:
            output_image_file_string = fig_data['output_image_file_string']

    print('Saving dose response figure to: %s' % output_image_file_string)
    dir_name = os.path.dirname(output_image_file_string)
    if (not os.path.isdir(dir_name)):
        os.makedirs(dir_name)
    fig.savefig(output_image_file_string)
    plt.close()

    # Save the data as an excel file
    if (fig_data['relative_to'] == 'this_file'):
        output_file_string = os.path.join(base_folder,
                                          fig_data['output_data_file_string'])
    else:
        output_file_string = fig_data['output_data_file_string']
    print('Writing dose reponse data to %s' % output_file_string)
    r.to_excel(output_file_string,
               engine='openpyxl',
               index=False)