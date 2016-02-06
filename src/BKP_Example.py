'''
Created on Feb 5, 2016

@author: tgack
'''
import BKPrecision_8502

def test(cmd, results):
    if results:
        print cmd, "failed:"
        print "  ", results
        exit(1)
    else:
        print cmd

if __name__ == '__main__':
    
    
    load = BKPrecision_8502.BKPrecision_8502("/dev/ttyUSB0", 4800, 0)

    print "Time from DC Load =", load.TimeNow()
    
    test("Set to remote control", load.SetRemoteControl())
    #test("Set CR resistance at 8.75 ohms", load.SetCRResistance(8.75))
    test("Set max current to 3 A", load.SetmaxCurrent(3))
    test("Set CC current to 0.869A", load.SetCCCurrent(0.869))
    test("Set load mode to CR", load.SetMode("CC"))
    test("Turn the load on", load.TurnLoadOn())

    print "Settings:"
    print "  Mode                =", load.GetMode()
    print "  Max voltage         =", load.GetMaxVoltage()
    print "  Max current         =", load.GetMaxCurrent()
    print "  Max power           =", load.GetMaxPower()
    print "  CC current          =", load.GetCCCurrent()
    print "  CV voltage          =", load.GetCVVoltage()
    print "  CW power            =", load.GetCWPower()
    print "  CR resistance       =", load.GetCRResistance()
    print "  Load on timer time  =", load.GetLoadOnTimer()
    print "  Load on timer state =", load.GetLoadOnTimerState()
    print "  Trigger source      =", load.GetTriggerSource()
    print "  Function            =", load.GetFunction()
    
    """
    print "  Input values:" 
    values = load.GetInputValues()
    for value in values.split("\t"): print "    ", value
    print "  Product info:"
    values = load.GetProductInformation()
    for value in values.split("\t"): print "    ", value
    """
    
    test("Turn the load off", load.TurnLoadOff())
    
    
    test("Set to local control", load.SetLocalControl())
    
    
    
    
    
    
    