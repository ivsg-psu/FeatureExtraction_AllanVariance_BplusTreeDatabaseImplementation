%%%%%%%%%%%%%%%%%%% script_synthesizeNoise2TestBptree.m %%%%%%%%%%%%%%%%%%%
%% Purpose:
%   The purpose of this script is to compare AVAR estimated using FAVAR and
%   B+ tree organization of the data.
% 
% Author:  Satya Prasad
% Created: 2023/03/10

%% Prepare the workspace
clear all %#ok<CLALL>
close all
clc

%% Load data
test_signal  = readmatrix('test_data.csv'); % Sample signal
bpTree_WN    = readmatrix('bpTree_WNAVAR.csv'); % AVAR of white noise using B+ trees
bpTree_RW    = readmatrix('bpTree_RWAVAR.csv'); % AVAR of random walk using B+ trees
bpTree_WNpRW = readmatrix('bpTree_WNpRWAVAR.csv'); % AVAR of white noise + random walk using B+ trees

%% Define inputs and other parameters
rng('default') % set random seeds
power_spectral_density  = 0.0004; % PSD of white noise [unit^2 s]
random_walk_coefficient = 0.02; % [unit/sqrt(s)]
sampling_frequency      = 50; % [Hz]
number_of_time_steps    = 2^18+1;
confidence_coefficient  = 0.95;

% List of correlation intervals
p = floor(log2(number_of_time_steps-1));
list_of_correlation_intervals = 2.^(0:p-3)';

%% Plot for white noise
[avar_wn,lb_avar_wn,ub_avar_wn] = ...
    fcn_AVAR_avarEmpiricalConfidenceCurves(test_signal(:,2),...
    list_of_correlation_intervals,confidence_coefficient,'wn');

figure(01)
clf
width = 540; height = 448; right = 100; bottom = 100;
axis_position = [0.1325, 70.515/height, 0.7725, 307.32/height];
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(list_of_correlation_intervals,avar_wn,'b','Linewidth',1.2)
plot(list_of_correlation_intervals,lb_avar_wn,'b--','Linewidth',1)
plot(list_of_correlation_intervals,ub_avar_wn,'b-.','Linewidth',1)
plot(bpTree_WN(2:end,3),bpTree_WN(2:end,2),'m','Linewidth',1.2)
set(gca,'Position',axis_position,'xtick',[1e0 1e2 1e4],...
    'XScale','log','YScale','log','Fontsize',13)
legend('FAVAR Estimate',[num2str(100*confidence_coefficient) '$\%$ LB'],...
       [num2str(100*confidence_coefficient) '$\%$ UB'],'B\textsuperscript{+}-tree Estimate',...
       'NumColumns',2,'Location','best','Interpreter','latex','FontSize',13)
ylabel('Allan Variance $[Unit^2]$','Interpreter','latex','FontSize',18)
xlabel('Correlation Interval $[Number \: of \: Samples]$',...
       'Interpreter','latex','FontSize',18)
ylim([1e-8 1e-1])
ax1 = gca;
axes('Position',axis_position,'XAxisLocation','top',...
     'xLim',ax1.XLim/sampling_frequency,'XScale','log',...
     'xtick',[1e-1 1e1 1e3],'ytick',[],...
     'Color','none','Fontsize',13,'Box','off');
ax2 = gca;
xlabel(ax2,'Correlation Time $[s]$','Interpreter','latex','FontSize',18)

%% Plot for random walk
[avar_rw,lb_avar_rw,ub_avar_rw] = ...
    fcn_AVAR_avarEmpiricalConfidenceCurves(test_signal(:,3),...
    list_of_correlation_intervals,confidence_coefficient,'rw');

figure(02)
clf
width = 540; height = 448; right = 100; bottom = 100;
axis_position = [0.1325, 70.515/height, 0.7725, 307.32/height];
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(list_of_correlation_intervals,avar_rw,'b','Linewidth',1.2)
plot(list_of_correlation_intervals,lb_avar_rw,'b--','Linewidth',1)
plot(list_of_correlation_intervals,ub_avar_rw,'b-.','Linewidth',1)
plot(bpTree_RW(2:end,3),bpTree_RW(2:end,2),'m','Linewidth',1.2)
set(gca,'Position',axis_position,'xtick',[1e0 1e2 1e4],...
    'XScale','log','YScale','log','Fontsize',13)
legend('FAVAR Estimate',[num2str(100*confidence_coefficient) '$\%$ LB'],...
       [num2str(100*confidence_coefficient) '$\%$ UB'],'B\textsuperscript{+}-tree Estimate',...
       'NumColumns',2,'Location','best','Interpreter','latex','FontSize',13)
ylabel('Allan Variance $[Unit^2]$','Interpreter','latex','FontSize',18)
xlabel('Correlation Interval $[Number \: of \: Samples]$',...
       'Interpreter','latex','FontSize',18)
ylim([1e-6 1e1])
ax1 = gca;
axes('Position',axis_position,'XAxisLocation','top',...
     'xLim',ax1.XLim/sampling_frequency,'XScale','log',...
     'xtick',[1e-1 1e1 1e3],'ytick',[],...
     'Color','none','Fontsize',13,'Box','off');
ax2 = gca;
xlabel(ax2,'Correlation Time $[s]$','Interpreter','latex','FontSize',18)

%% Plot for random walk + white noise
avar_wnPrw = fcn_AVAR_favar(test_signal(:,4),list_of_correlation_intervals);

matrix_avar = NaN(p-2,100);
for i = 1:100
    white_noise  = fcn_AVAR_generateWhiteNoise(power_spectral_density,...
                   sampling_frequency,number_of_time_steps); % White noise
    random_walk  = fcn_AVAR_generateRandomWalk(random_walk_coefficient,...
                   sampling_frequency,number_of_time_steps); % Random walk
    noise_signal = white_noise + random_walk;
    matrix_avar(:,i) = fcn_AVAR_favar(noise_signal,list_of_correlation_intervals);
end % NOTE: END FOR loop
dof_estimate = 2*(mean(matrix_avar,2).^2)./var(matrix_avar,1,2);

chi1_squared = icdf('Chisquare',0.5*(1-confidence_coefficient),dof_estimate);
chi2_squared = icdf('Chisquare',0.5*(1+confidence_coefficient),dof_estimate);

% calculate lower and upper confidence surfaces using eq.(31)
lb_avar_wnPrw = (dof_estimate.*avar_wnPrw)./chi2_squared;
ub_avar_wnPrw = (dof_estimate.*avar_wnPrw)./chi1_squared;

figure(03)
clf
width = 540; height = 448; right = 100; bottom = 100;
axis_position = [0.1325, 70.515/height, 0.7725, 307.32/height];
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(list_of_correlation_intervals,avar_wnPrw,'b','Linewidth',1.2)
plot(list_of_correlation_intervals,lb_avar_wnPrw,'b--','Linewidth',1)
plot(list_of_correlation_intervals,ub_avar_wnPrw,'b-.','Linewidth',1)
plot(bpTree_WNpRW(2:end,3),bpTree_WNpRW(2:end,2),'m','Linewidth',1.2)
set(gca,'Position',axis_position,'xtick',[1e0 1e2 1e4],...
    'XScale','log','YScale','log','Fontsize',13)
legend('FAVAR Estimate',[num2str(100*confidence_coefficient) '$\%$ LB'],...
       [num2str(100*confidence_coefficient) '$\%$ UB'],'B\textsuperscript{+}-tree Estimate',...
       'NumColumns',2,'Location','best','Interpreter','latex','FontSize',13)
ylabel('Allan Variance $[Unit^2]$','Interpreter','latex','FontSize',18)
xlabel('Correlation Interval $[Number \: of \: Samples]$',...
       'Interpreter','latex','FontSize',18)
ylim([1e-4 10^0.5])
ax1 = gca;
axes('Position',axis_position,'XAxisLocation','top',...
     'xLim',ax1.XLim/sampling_frequency,'XScale','log',...
     'xtick',[1e-1 1e1 1e3],'ytick',[],...
     'Color','none','Fontsize',13,'Box','off');
ax2 = gca;
xlabel(ax2,'Correlation Time $[s]$','Interpreter','latex','FontSize',18)

figure(04)
clf
width = 400; height = 500; right = 100; bottom = 100;
axis_position = [20/width, 20/height, 307.32/width, 417.15/height];
set(gcf, 'position', [right, bottom, width, height])
hold on
grid on
plot(avar_wnPrw,list_of_correlation_intervals,'b','Linewidth',1.2)
set(gca,'Position',axis_position,'XScale','log','YScale','log',...
    'xticklabel',[],'yticklabel',[],'Fontsize',13)
xlim([1e-4 10^0.5])
ax1 = gca;
axes('Position',axis_position,'XAxisLocation','top','xLim',ax1.XLim,'XScale','log',...
    'YAxisLocation','right','yLim',ax1.YLim,'YScale','log',...
    'Color','none','Fontsize',13,'Box','off');
ax2 = gca;
xlabel(ax2,'Allan Variance $[Unit^2]$','Interpreter','latex','FontSize',18)
ylabel(ax2,'Correlation Interval $[Number \: of \: Samples]$',...
    'Interpreter','latex','FontSize',18)
