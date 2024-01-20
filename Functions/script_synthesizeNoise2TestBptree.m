%%%%%%%%%%%%%%%%%%% script_synthesizeNoise2TestBptree.m %%%%%%%%%%%%%%%%%%%
%% Purpose:
%   The purpose of this script is to synthesize white noise, random walk, 
%   and random walk + white noise to test AVAR estimation using B+ trees.
% 
% Author:  Satya Prasad
% Created: 2023/03/10

%% Prepare the workspace
clear all %#ok<CLALL>
close all
clc

%% Define inputs and other parameters
rng('default') % set random seeds
power_spectral_density  = 0.0004; % PSD of white noise [unit^2 s]
random_walk_coefficient = 0.02; % [unit/sqrt(s)]
sampling_frequency      = 50; % [Hz]
number_of_time_steps    = 2^18+1;
flag_save               = false;

%% Synthesize noise: White noise, Random walk
time_vector = (0:number_of_time_steps-1)'/sampling_frequency;
white_noise = fcn_AVAR_generateWhiteNoise(power_spectral_density,...
              sampling_frequency,number_of_time_steps); % White noise
random_walk = fcn_AVAR_generateRandomWalk(random_walk_coefficient,...
              sampling_frequency,number_of_time_steps); % Random walk
test_signal = white_noise + random_walk;

%% Save the data as csv file
if flag_save
    test_data.Time         = time_vector;
    test_data.WhiteNoise   = white_noise;
    test_data.RandomWalk   = random_walk;
    test_data.White_Random = test_signal;
    writetable(struct2table(test_data),'test_data.csv');
end % NOTE: END IF statement 'flag_save'

%% Plot the results
mag_lb    = min(white_noise(1:2000*sampling_frequency+1));
mag_ub    = max(white_noise(1:2000*sampling_frequency+1));
mag_range = mag_ub-mag_lb;
figure(01)
clf
width = 540; height = 400; right = 100; bottom = 100;
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(time_vector,white_noise,'k.','Markersize',2)
set(gca,'Fontsize',13)
xlabel('Time $[s]$','Interpreter','Latex','Fontsize',18)
ylabel('Amplitude $[Unit]$','Interpreter','Latex','Fontsize',18)
ylim([mag_lb-0.1*mag_range mag_ub+0.1*mag_range])
xlim([0, 2000])

mag_lb    = min(test_signal(1:2000*sampling_frequency+1));
mag_ub    = max(test_signal(1:2000*sampling_frequency+1));
mag_range = mag_ub-mag_lb;
figure(02)
clf
width = 540; height = 400; right = 100; bottom = 100;
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(time_vector,random_walk,'k')
set(gca,'Fontsize',13)
xlabel('Time $[s]$','Interpreter','Latex','Fontsize',18)
ylabel('Amplitude $[Unit]$','Interpreter','Latex','Fontsize',18)
ylim([mag_lb-0.1*mag_range mag_ub+0.1*mag_range])
xlim([0, 2000])

figure(03)
clf
width = 540; height = 400; right = 100; bottom = 100;
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(time_vector,test_signal,'k.','Markersize',2)
set(gca,'Fontsize',13)
xlabel('Time $[s]$','Interpreter','Latex','Fontsize',18)
ylabel('Amplitude $[Unit]$','Interpreter','Latex','Fontsize',18)
ylim([mag_lb-0.1*mag_range mag_ub+0.1*mag_range])
xlim([0, 2000])
