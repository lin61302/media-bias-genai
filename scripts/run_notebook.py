"""Execute and export the analysis notebook with the active Python environment."""
from pathlib import Path
import sys, tempfile, json
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client.kernelspec import KernelSpecManager

root=Path(__file__).resolve().parents[1]
path=root/'notebooks/01_dashboard_and_measures.ipynb'
book=nbformat.read(path,as_version=4)
# Resolve the kernel to this interpreter rather than an unrelated system Python.
with tempfile.TemporaryDirectory() as temp:
    d=Path(temp)/'analysis';d.mkdir()
    (d/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Project analysis','language':'python'}))
    manager=KernelSpecManager(kernel_dirs=[temp])
    client=NotebookClient(book,timeout=180,kernel_name='analysis',resources={'metadata':{'path':str(root)}})
    client.create_kernel_manager()
    client.km.kernel_spec_manager=manager
    client.execute()
nbformat.write(book,path)
html,_=HTMLExporter(template_name='lab').from_notebook_node(book)
path.with_suffix('.html').write_text(html)
print('Executed notebook and exported HTML, figures and tables.')
