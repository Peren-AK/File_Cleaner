import os
import shutil
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

#それぞれの拡張子に対しファイルを割り当てる
file_type = {
    '.jpg': 'Images',
    '.jpeg': 'Images',
    '.png': 'Images',
    '.gif': 'Images',
    '.pdf': 'Documents',
    '.docx': 'Documents',
    '.doc': 'Documents',
    '.txt': 'Documents',
    '.xlsx': 'Documents',
    '.xls': 'Documents',
    '.pptx': 'Documents',
    '.zip': 'Compressed',
    '.rar': 'Compressed',
    '.gz': 'Compressed',
    '.mp4': 'Videos',
    '.mov': 'Videos',
    '.mp3': 'Music',
}

others_folder = 'Others'



#GUIから実行できるように設定
def GUI():
    #フォルダ選択
    def choose_folder():
        folder = filedialog.askdirectory(title='整理するフォルダを選んでください')
        if folder:
            target_path.set(folder)
        
    #実行
    def execute_organize():
        path = target_path.get()
        dry_run = dry_run_var.get()
        
        #フォルダが指定されていない時
        if not path:
            messagebox.showwarning('警告', 'フォルダを選択してください。')
            return
        
        #整理実行
        organize_folder(path, dry_run)
        
        if not dry_run:
            messagebox.showinfo('完了', 'ファイルの整理が完了しました!')
        
            #自動でウィンドウを閉じる
            root.quit()
            
            return
        
        messagebox.showinfo('完了', 'ドライランが終了しました。')
    
    root = tk.Tk()
    root.title('ファイル整理ツール')
    
    target_path = tk.StringVar()
    
    #ドライランON/OFF
    dry_run_var = tk.BooleanVar()
    
    #GUIを設定
    tk.Label(root, text='整理対象のフォルダ:').pack(pady=5)
    tk.Entry(root, textvariable=target_path, width=50).pack(padx=10)
    tk.Button(root, text='フォルダを選択', command=choose_folder).pack(pady=5)
    tk.Checkbutton(root, text='ドライラン（模擬移動)', variable=dry_run_var).pack()
    tk.Button(root, text='整理を実行', command=execute_organize).pack(pady=10)
    
    root.mainloop()



#整理実行部分
def organize_folder(target_path, dry_run):
    #対象ファイルへのpathオブジェクト
    path = Path(target_path)
    
    if not path.exists():
        print('対象のフォルダが存在しないようです。\nもう一度ファイルパスを確認してください。', file=sys.stderr)
        return
    
    #フォルダ内のファイル等を読み込む
    try:
        items = list(path.iterdir())
        
    except Exception as e:
        print('フォルダ読み込み時にエラーが発生しました。 - {}'.format(e), file=sys.stderr)
        return
        
    if not items:
        print('対象フォルダは空です。')
        return
    
    for item in items:
        #.DS_Storeの処理をスキップ
        if item.name == '.DS_Store':
            continue
        
        #対象がファイルの場合
        if item.is_file():
            source_file_path = item
            file_name = source_file_path.name
            base_name = source_file_path.stem
            
            #拡張子取得
            extension = source_file_path.suffix.lower()
            
            target_folder = file_type.get(extension, others_folder)

            target_folder_path = path / target_folder

            #移動先のフォルダがない場合作成
            if not dry_run:
                if not target_folder_path.exists():
                    try:
                        target_folder_path.mkdir(parents=True, exist_ok=True)

                    except Exception as e:
                        print('フォルダ作成時にエラーが発生しました。 - {}'.format(e), file=sys.stderr)
                        continue
                
            target_file_path = target_folder_path / file_name    

            #移動先にもともとファイルが存在する場合、名前を変更
            numbering = 0
            probable_filename = file_name
            while target_file_path.exists():
                numbering += 1
                old_file_basename = base_name
                old_filename = probable_filename
                
                #無限ループ防止
                if numbering > 1000:
                    print('{}の重複を回避するため、ファイル名の変更を試みましたが失敗しました。'.format(file_name))
                    last_filename = None
                    break
                
                filename = '{0}_{1}{2}'.format(old_file_basename, numbering, extension)
                target_file_path = target_folder_path / filename  
                probable_filename = target_file_path.name
                print('ファイルが重複するため、ファイル名を変更しました。 - {0} => {1}'.format(old_filename, filename))  

            last_filename = probable_filename

            if dry_run:
                print('[ドライラン]ファイル名{0}を{1}に移動します。'.format(last_filename, target_folder))
                continue
            
            #ファイルを移動する
            try:
                shutil.move(source_file_path, target_file_path)
                print('ファイルを移動しました。 - {0} => {1}'.format(last_filename, target_folder))

            except Exception as e:
                print('ファイル移動時にエラーが発生しました。 - {}'.format(e), file=sys.stderr)
                continue
     
    if not dry_run:   
        print('ファイルの整理が終了しました。')
        return

    print('ドライランが終了しました。')
    
    

if __name__ == '__main__':
    GUI()