

import Tkinter as tk
import _winreg as reg
from subprocess import Popen

# from http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)            
        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)
        
        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)
        
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)
        
        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
        
        def _on_mousewheel(event):
            canvas.yview_scroll(-1*(event.delta/120), tk.UNITS)
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
        
        return

class VarCheckbutton(tk.Checkbutton):
    def  __init__(self, master=None, **kw):
        self.var = tk.IntVar()
        kw['variable'] = self.var
        tk.Checkbutton.__init__(self, master, kw)
        
class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.session_names = []
        
        control_frame = tk.Frame(self)
        tk.Button(control_frame, text="Refresh", width=10,
                  command=lambda:self.refresh(self.btn_frame.interior)).grid(padx=10)
        tk.Button(control_frame, text="Launch", width=10,
                  command=lambda:self.launch(self.btn_frame.interior)).grid(padx=10, row=0, column=1)
        control_frame.pack(pady=20)
        
        self.btn_frame = VerticalScrolledFrame(self)
        self.refresh(self.btn_frame.interior)
        self.btn_frame.pack(pady=10, fill=tk.BOTH, expand=tk.TRUE)
            
    def get_sessions(self):
        aReg = reg.ConnectRegistry(None, reg.HKEY_CURRENT_USER)
        aKey = reg.OpenKey(aReg, r"Software\SimonTatham\PuTTY\Sessions")
        self.session_names = []
        for i in range(1024):
            try:
                asubkey_name = reg.EnumKey(aKey, i)
                self.session_names.append(asubkey_name)
            except EnvironmentError:
                break
            
    def refresh(self, master):
        old_sessions = self.session_names
        self.get_sessions()
        if old_sessions != self.session_names:
            for item in master.winfo_children():
                item.destroy()
            self.draw_sessions(master)

    def draw_sessions(self, master):
        f = None
        for idx in range(len(self.session_names)):
            if (idx % 2) == 0:
                side = tk.LEFT
                if f:
                    f.pack()
                f = tk.Frame(master)
            else:
                side = tk.RIGHT
                
            text = self.session_names[idx]
            VarCheckbutton(f, text=text, indicatoron=0, relief=tk.RAISED,
                           height=2, width=14).pack(padx=10, pady=5, side=side)
        if f:
            f.pack()
                
    def launch(self, frame):
        for child_frame in frame.winfo_children():
            for button in child_frame.winfo_children():
                if button.var.get():
                    Popen(['putty.exe', '-load', button['text']])
                    button.deselect()
                    
def main(argv):
    top = tk.Tk()
    top.title('PuTTY Launcher')
    top.geometry('275x400')
    
    try:
        app = App(master=top)
    except:
        print 'didn\'t make app' 
    app.pack(fill=tk.BOTH, expand=tk.TRUE)
    top.mainloop()

if __name__ == '__main__':
    import sys
    main(sys.argv)
