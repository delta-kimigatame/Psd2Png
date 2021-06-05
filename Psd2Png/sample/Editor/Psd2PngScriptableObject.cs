using System;
using System.Collections;
using UnityEngine;

public class Psd2PngScriptableObject : ScriptableObject
{
    [SerializeField]
    private string psdPath;
    [SerializeField]
    private string outputDir;
    [SerializeField]
    private string[] outputPaths;

    public string PsdPath {
        get => psdPath;
#if UNITY_EDITOR
        set => psdPath = value;
#endif
    }
    public string OutputDir {
        get => outputDir;
#if UNITY_EDITOR
        set => outputDir = value;
#endif
    }
    public string[] OutputPaths {
        get => outputPaths;
#if UNITY_EDITOR
        set => outputPaths = value;
#endif
    }
}
