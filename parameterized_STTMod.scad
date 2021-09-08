// Remix of Smart compact temperature calibration tower by gaaZolee
// This OpenSCAD script uses the components in original design to generate a parametrizable tower (tmin, tmax, tstep)
//
// V3 2018-11-29
// Restored the possibility of choosing the order of the temperatures from low to high or high to low.

// Pertti Tolonen 2018

// Configure the min&max temp + floor-to-floor temp step 
// NOTICE: sign of tstep is recalculated, no need to provide a negative value
tfirst=205;
tlast=195;
tstep=2;

tstep1 = tfirst>tlast ?  abs(tstep)*-1 : abs(tstep);
// Instantiate the "base" and move it to origin
translate([-9,-9,0])
import("SmartTemperatureTower_Stand.stl");

// Define module for the "floor"
module TempFloor(temp){
difference(){
union(){
    translate([-113,-100,0]) // move to origin
    import("SmartTemperatureTower_TempFloor.stl");

}
// Add parametrized text
rotate([90,0,0])
    translate([12,1.5,-0.5])
linear_extrude(height=1,center=false)
text(str(temp),size=3);
}
}

// The top-level code
floors=abs((tfirst-tlast)/tstep1)+1; // Calculate # floors
 if (floors < 2)
 {
    echo ("There must be at least two floors to be useful ! ");
 }
else
{
    union()
    {
        difference() 
        {
            TempFloor(str(tfirst));
            translate([-2,-1,-1])
            cube([40,15,1.5]);
        }
        for(i=[1:(floors-1)])
        {
            translate([0,0,10*i])
            TempFloor(str(tfirst+i*tstep1));
        }
    }
}