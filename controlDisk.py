import sys, subprocess

def control(action, pool, disk):
    cmdline=['zpool', action, pool, disk]
    result=subprocess.run(cmdline, capture_output=True)
    error = str(result.stderr.decode()).replace('\n\n','\n').split('\n')
    status = ''
    if (error[0] == ''):
        status = 'OK'
    else:
        status = 'ERROR'
    return {'Status': status, 'Error': error}
    
if __name__=='__main__':
    action = sys.argv[1]
    pool = sys.argv[2]
    disk = sys.argv[3]
    print(control(action, pool, disk))
