x_axis_start = 1050;
x_axis_stop = 1450;

aaa = zeros(50);
gt = 700:10:990;
Alcenter_1 = 1110;
FWHM_1_up = 80;
FWHM_1_low = 60;
Alcenter_2 = 1180;
FWHM_2_up = 90;
FWHM_2_low = 75;
Alcenter_3 = 1300;
FWHM_3_up = 90;
FWHM_3_low = 70;
Alcenter_4 = 1430;
FWHM_4_up = 70;
FWHM_4_low = 60;
Temperature = 'RT';

%subtitle(strcat(sprintf('BEDF-2 Emission Gaussian Composition Result: \n BAC-Al @'), num2str(Alcenter_1), ' nm, BAC-1180 @ ', num2str(Alcenter_2), ' nm, BAC-P @ ', num2str(Alcenter_3), ' nm, BAC-Si @ ', num2str(Alcenter_4), ' nm, ', Temperature));
for row = 2:1:30
    fo = fitoptions('gauss4','upper',[Inf Alcenter_1 FWHM_1_up Inf Alcenter_2 FWHM_2_up Inf Alcenter_3 FWHM_3_up Inf Alcenter_4 FWHM_4_up],'lower',[0 Alcenter_1  FWHM_1_low 0 Alcenter_2 FWHM_2_low 0 Alcenter_3 FWHM_3_low 0 Alcenter_4 FWHM_4_low],'StartPoint',[0.005 Alcenter_1 50 0.005 Alcenter_2 50 0.005 Alcenter_3 50 0.005 Alcenter_4 50],'Robust','LAR');
    options = fo ;
    bac_al = mygau(z(:,1),f.a1,f.b1,f.c1);
    
    [f,gof]= fit(z(:,1),z(:,row),'gauss4',options);
    %gof;
    subplot(10,3,row-1);
    plot(f,z(:,1),z(:,row));
    hold on
    plot(f,z(:,1),mygau(z(:,1),f.a1,f.b1,f.c1),'--')
    plot(f,z(:,1),mygau(z(:,1),f.a2,f.b2,f.c2),'--')
    plot(f,z(:,1),mygau(z(:,1),f.a3,f.b3,f.c3),'--')
    plot(f,z(:,1),mygau(z(:,1),f.a4,f.b4,f.c4),'--')
    hold off
    
    xlim([x_axis_start x_axis_stop])
    %xlabel('Wavelength (nm)')
    %ylabel('Intensity (a.u.)')
    set(gca, 'XTick', [x_axis_start:100:x_axis_stop])
    %set(gca,'xlabel','Wavelength (nm)');
    %set(gca,'yticklabel','Emissoin intensity (a.u.)');
    
    set(legend(),'visible','off');
    title(strcat('Pump',{' '}, num2str(gt(row)),' nm, RMSE ',{' '}, num2str(round(gof.rmse,3))));
    
    %result = [f.a1;f.b1;f.c1;f.a2;f.b2;f.c2;gof.rsquare];
    aaa(1,row-1) = f.a1;
    aaa(2,row-1) = f.b1;
    aaa(3,row-1) = f.c1;
    aaa(4,row-1) = f.a2;
    aaa(5,row-1) = f.b2;
    aaa(6,row-1) = f.c2;
    aaa(7,row-1) = f.a3;
    aaa(8,row-1) = f.b3;
    aaa(9,row-1) = f.c3;
    aaa(10,row-1) = f.a4;
    aaa(11,row-1) = f.b4;
    aaa(12,row-1) = f.c4;
    aaa(13,row-1) = gof.rsquare;
    aaa(14,row-1) = gof.rmse;
    gof.rsquare
end