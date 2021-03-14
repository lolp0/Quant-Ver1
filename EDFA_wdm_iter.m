function [y_sig_dBm y_ase_dBm y_pmp_dBm] = EDFA_wdm_iter(Psig0_dBm,Pase0_dBm,P_in_pump,lambda)
    % Main function to model Erbium Doped Fibre Amplifier(EDFA)
    % close; clear; clc;
    format long E;
    %% defining the EDFA Material parameters & universal constants
    h = 6.626068e-34;                  % Planck's constant
    c = 3e8;                           % speed of light in vacuum
    gamma_s = 0.8;                     % mode overlap factor for signal & ASE 
    gamma_p = 0.85;                    % modde overlap factor for pump
    A_s = 5.26e-12;                    % effective area for signal
    A_p = 3.36e-12;                    % effective area for pump
    N = 1.0e25;                        % total erbium dopant concentration
    tau = 10e-3;                       % metastable carrier lifetime
    %L = 4.2;                          % length of fibre for pump @ 980 nm
    L = 6.8;                           % length of fibre for pump @ 1470 nm
    del_z = 0.2;                       % smalest length segment considered
    Nz = L/del_z;                      % total no. of segments
    Nch = length(lambda);              % total no. of wavelengths
    del_neu = 250e9;                   % frequency spacing of 2 nm 
    
    %% Beginning to solve differential equations for carrier density, signal power, pump power & ASE power
    N2 = zeros(1,Nz);                       % population density in the upper state
    N1 = zeros(1,Nz);                       % population density in the ground state
    Psp = zeros(Nch,Nz);                    % signal power in +ve z direction
    Ppp = zeros(1,Nz);                      % pump power in +ve z direction
    Pap = zeros(Nch,Nz);                    % ASE power in +ve z direction
    Pan = zeros(Nch,Nz);                    % ASE power in -ve z direction
    
    Psat = 20;                              % saturation power of EDFA (dBm)
    Psat = 1e-3*10.^(Psat/10);
    P_in_sig = 1e-3*10.^(Psig0_dBm/10);     % signal input power to the EDFA
    %P_in_ase = 1e-3*10.^(Pase0_dBm/10);    % ASE input power to the EDFA
    P_in_ase = zeros(length(Pase0_dBm));   
    %P_in_pump = 100e-3;                    % pump input power
    lambda_p = 980e-9;                      % pump wavelength
    neu_p = c/lambda_p;                     % pump frequency
    neu_s = c./lambda;                      % signal frequencies
    sigma_p_a = 2.58e-25;                   % pump absorption cross-section @ 980 nm
    sigma_p_e = 0;                          % pump emission cross-section @ 980 nm
    
    for mm = 1:1:(2*Nz),
    % starting the iteration for all the segments of EDFA
        for j = 1:1:Nz,
            % evaluating the values of carrier densities in upper & lower states
            sig_xx = 0;
            sig_yy = 0;                    % initializing some useful variables for ease of computation
            ase_xx = 0;
            ase_yy = 0;
            pmp_xx = 0;
            pmp_yy = 0;
            if(j == 1),
                pmp_xx = pmp_xx+(sigma_p_a)*(P_in_pump*gamma_p/A_p)/(h*neu_p);             % computing pump term in numerator for 1st segment
                pmp_yy = pmp_yy+(sigma_p_a+sigma_p_e)*(P_in_pump*gamma_p/A_p)/(h*neu_p);   % computing pump term in denominator for 1st segment
                for i = 1:1:Nch,                                                           % computing signal term in numerator for 1st segment
                    sig_xx = sig_xx+(sigma_abs(lambda(i))*(P_in_sig(i)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing signal term in denominator for 1st segment
                    sig_yy = sig_yy+(sigma_abs(lambda(i))+sigma_ems(lambda(i)))*(P_in_sig(i)*gamma_s/A_s)/(h*neu_s(i));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in numerator for 1st segment
                    ase_xx = ase_xx+(sigma_abs(lambda(i))*((P_in_ase(i)+Pan(i,j+1))*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in denominator for 1st segment
                    ase_yy = ase_yy+((sigma_abs(lambda(i))+sigma_ems(lambda(i)))*((P_in_ase(i)+Pan(i,j+1))*gamma_s/A_s)/(h*neu_s(i)));
                end
            end
            
            if(j > 1 && j < Nz),
                pmp_xx = (sigma_p_a)*(Ppp(j-1)*gamma_p/A_p)/(h*neu_p);                     % computing pump term in numerator for 2nd segment onwards
                pmp_yy = (sigma_p_a+sigma_p_e)*(Ppp(j-1)*gamma_p/A_p)/(h*neu_p);           % computing pump term in denominator for 2nd segment onwards
                for i = 1:1:Nch,                                                           % computing signal term in numerator for 1st segment
                    sig_xx = sig_xx+(sigma_abs(lambda(i))*(Psp(i,j-1)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing signal term in denominator for 1st segment
                    sig_yy = sig_yy+((sigma_abs(lambda(i))+sigma_ems(lambda(i)))*(Psp(i,j-1)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in numerator for 1st segment
                    ase_xx = ase_xx+(sigma_abs(lambda(i))*((Pap(i,j-1)+Pan(i,j+1))*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in denominator for 1st segment
                    ase_yy = ase_yy+((sigma_abs(lambda(i))+sigma_ems(lambda(i)))*((Pap(i,j-1)+Pan(i,j+1))*gamma_s/A_s)/(h*neu_s(i)));
                end
            end
                
            if(j == Nz),
                pmp_xx = (sigma_p_a)*(Ppp(j-1)*gamma_p/A_p)/(h*neu_p);                     % computing pump term in numerator for 2nd segment onwards
                pmp_yy = (sigma_p_a+sigma_p_e)*(Ppp(j-1)*gamma_p/A_p)/(h*neu_p);           % computing pump term in denominator for 2nd segment onwards
                for i = 1:1:Nch,                                                           % computing signal term in numerator for 1st segment
                    sig_xx = sig_xx+(sigma_abs(lambda(i))*(Psp(i,j-1)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing signal term in denominator for 1st segment
                    sig_yy = sig_yy+((sigma_abs(lambda(i))+sigma_ems(lambda(i)))*(Psp(i,j-1)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in numerator for 1st segment
                    ase_xx = ase_xx+(sigma_abs(lambda(i))*((Pap(i,j-1)+0)*gamma_s/A_s)/(h*neu_s(i)));
                end
                for i = 1:1:Nch,                                                           % computing ASE term in denominator for 1st segment
                    ase_yy = ase_yy+((sigma_abs(lambda(i))+sigma_ems(lambda(i)))*((Pap(i,j-1)+0)*gamma_s/A_s)/(h*neu_s(i)));
                end
            end
        
            N2(j) = ((pmp_xx+sig_xx+ase_xx)/(pmp_yy+sig_yy+ase_yy+(1/tau)))*N;             % carrier densities in upper state
            N1(j) = N-N2(j);                                                               % carrier densities in lower state
        end
        
        for j = 1:1:Nz,
        % solving the differential equation for pump power in +ve z direction
            if(j == 1),
                Ppp(j) = P_in_pump+(N2(j)*sigma_p_e-N1(j)*sigma_p_a)*gamma_p*P_in_pump*del_z;
            else
                Ppp(j) = Ppp(j-1)+(N2(j)*sigma_p_e-N1(j)*sigma_p_a)*gamma_p*Ppp(j-1)*del_z;
            end
            
        % solving the differential equation for signal power in +ve z direction
            if(j == 1),
                for i = 1:1:Nch,
                    Psp(i,j) = P_in_sig(i)+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*P_in_sig(i)*del_z/(1+P_in_sig(i)/Psat));
                end
            else
                for i = 1:1:Nch,
                    Psp(i,j) = Psp(i,j-1)+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*Psp(i,j-1)*del_z/(1+Psp(i,j-1)/Psat));
                end
            end
        
        % solving the differential equation for ASE power in +ve z direction
            if(j == 1),
                for i = 1:1:Nch,
                    Pap(i,j) = P_in_ase(i)+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*P_in_ase(i)/(1+P_in_ase(i)/Psat)+2*N2(j)*sigma_ems(lambda(i))*gamma_s*h*neu_s(i)*del_neu)*del_z;
                end
            else
                for i = 1:1:Nch,
                    Pap(i,j) = Pap(i,j-1)+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*Pap(i,j-1)/(1+Pap(i,j-1)/Psat)+2*N2(j)*sigma_ems(lambda(i))*gamma_s*h*neu_s(i)*del_neu)*del_z;
                end
            end
           
        % solving the differential equation for ASE power in -ve z direction
            if(j == Nz),
                for i = 1:1:Nch,
                    Pan(i,j) = 0+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*0+2*N2(j)*sigma_ems(lambda(i))*gamma_s*h*neu_s(i)*del_neu)*del_z;
                end
            else
                for i = 1:1:Nch,
                    Pan(i,j) = Pan(i,j+1)+((N2(j)*sigma_ems(lambda(i))-N1(j)*sigma_abs(lambda(i)))*gamma_s*Pan(i,j+1)/(1+Pan(i,j+1)/Psat)+2*N2(j)*sigma_ems(lambda(i))*gamma_s*h*neu_s(i)*del_neu)*del_z;
                end
            end
        end
        Ptot = Psp+Pap+Pan;
    end
    
    y_sig_dBm = 10*log10(Psp(:,Nz)/1e-3);                 % returning the signal powers in all channels at EDFA output
    y_ase_dBm = 10*log10(Pap(:,Nz)/1e-3);                 % returning the ASE powers in all channels at EDFA output
    y_pmp_dBm = 10*log10(Ppp(Nz)/1e-3);                   % returning the pump powers at EDFA output
