import os
import glob

res = glob.glob('*/migrations/*', recursive=True)
for file_path in res:    
    if file_path.endswith('__pycache__'):
        file_path = file_path+'/*'
        sub_res = glob.glob(file_path)
        for file_path in sub_res:
            os.remove(file_path)
    elif not file_path.endswith('__init__.py'):
        os.remove(file_path)
sub_res = glob.glob('/**/*.pyc')
for file_path in sub_res:
    os.remove(file_path)
print ('done')

# from pathlib import Path
# for file_obj in Path('.').glob('*/migrations/*.py'):
#     if file_obj.name != '__init__.py':
#         try:
#             os.remove(file_obj._str)
#         except:
#             print(file_obj)