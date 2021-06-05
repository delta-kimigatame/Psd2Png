using UnityEngine;
using UnityEditor;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Collections.Generic;

public class Psd2PngWindow : EditorWindow
{
    [MenuItem("Editor/Psd2Png")]
    private static void Create()
    {
        GetWindow<Psd2PngWindow>("Psd2Png");
    }
    private Psd2PngScriptableObject so;
    private void OnGUI()
    {
        if (so == null)
        {
            so = ScriptableObject.CreateInstance<Psd2PngScriptableObject>();

        }
        EditorGUILayout.Space();
        if (GUILayout.Button("初期化"))
        {
            so.PsdPath = "";
            so.OutputDir = "";
            so.OutputPaths = new List<string>().ToArray();
        }
        EditorGUILayout.Space();
        GUILayout.Box("", GUILayout.ExpandWidth(true), GUILayout.Height(1));
        EditorGUILayout.Space();
        EditorGUILayout.LabelField("Pngに変換したいPsdのパス");
        EditorGUI.indentLevel++;
        so.PsdPath = EditorGUILayout.TextField("Psdパス", so.PsdPath);
        so.OutputDir = EditorGUILayout.TextField("出力パス(空欄可)", so.OutputDir);
        EditorGUILayout.LabelField("空欄の場合、psdと同じフォルダにpsdと同じ名前のフォルダが生成されます");
        if (GUILayout.Button("pngに分割"))
        {
            SimplePsd2PngButton();
        }
        EditorGUILayout.Space();
        GUILayout.Box("", GUILayout.ExpandWidth(true), GUILayout.Height(1));
        EditorGUILayout.Space();

        EditorGUI.indentLevel=0;
        EditorGUILayout.LabelField("出力結果を確認してからpngに変換する場合はこちら");
        EditorGUILayout.LabelField("空欄が1行でもあると無視されます。");
        if (GUILayout.Button("レイヤー名取得"))
        {
            GetOutList();
        }
        for (int i = 0; i < so.OutputPaths.Length; i++)
        {
            so.OutputPaths[i] = EditorGUILayout.TextField("pngパス" + i.ToString(), so.OutputPaths[i]);
        }
        if (GUILayout.Button("pngに分割"))
        {
            Psd2PngButton();
        }
    }

    private Process ProcessInitCommon()
    {
        Process proc = new Process();
        proc.StartInfo.FileName = ".\\Assets\\Editor\\Binary\\Psd2Png.exe";
        proc.StartInfo.CreateNoWindow = true;
        proc.StartInfo.UseShellExecute = false;
        proc.StartInfo.StandardErrorEncoding = Encoding.GetEncoding("x-ms-cp932");
        proc.StartInfo.RedirectStandardError = true;
        return proc;

    }

    private void OutputLog(string stderr)
    {
        foreach (string log in stderr.Split('\n'))
        {
            if (log.StartsWith("ERROR"))
            {
                UnityEngine.Debug.LogError(log);
            }
            else if (log.StartsWith("INFO"))
            {
                UnityEngine.Debug.Log(log);
            }
            else if (log.StartsWith("DEBUG"))
            {
                UnityEngine.Debug.Log(log);
            }
        }
    }

    private void SimplePsd2PngButton()
    {
        Process proc = ProcessInitCommon();
        if (so.OutputDir == "")
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert";
        }
        else
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert --outdir=" + so.OutputDir;
        }
        proc.Start();
        string stderr = proc.StandardError.ReadToEnd();
        proc.WaitForExit();
        OutputLog(stderr);
    }
    private void Psd2PngButton()
    {
        Process proc = ProcessInitCommon();
        if (so.OutputDir == "")
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert";
        }
        else
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert --outdir=" + so.OutputDir;
        }
        string joinpaths = "" + string.Join(" ", so.OutputPaths) + "";
        UnityEngine.Debug.Log(joinpaths);
        proc.StartInfo.Arguments += " " + joinpaths;
        UnityEngine.Debug.Log(proc.StartInfo.Arguments);

        proc.Start();
        string stderr = proc.StandardError.ReadToEnd();
        proc.WaitForExit();
        OutputLog(stderr);
    }

    private void GetOutList()
    {
        Process proc = ProcessInitCommon();
        if (so.OutputDir == "")
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert --outlist";
        }
        else
        {
            proc.StartInfo.Arguments = so.PsdPath + " --force --noalert --outlist --outdir=" + so.OutputDir;
        }

        string stderr = null;
        proc.ErrorDataReceived += new DataReceivedEventHandler((sender, e) =>
        {
            stderr += "\n" + e.Data;
        });
        proc.StartInfo.RedirectStandardOutput = true;
        proc.StartInfo.StandardOutputEncoding = Encoding.GetEncoding("x-ms-cp932");
        proc.Start();
        proc.BeginErrorReadLine();
        string stdout = proc.StandardOutput.ReadToEnd();
        proc.WaitForExit();
        OutputLog(stderr);
        UnityEngine.Debug.Log(stdout);
        List<string> paths = new List<string>();
        foreach (string path in stdout.Split('\n'))
        {
            if (path != "")
            {
                paths.Add(path);
            }
        }
        so.OutputPaths = paths.ToArray();

    }
}
