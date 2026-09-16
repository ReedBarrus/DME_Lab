using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows.Forms;

namespace DmeHomeCapture
{
    internal static class HomeCaptureLauncher
    {
        private const string ServiceName = "home_capture_v0";

        [STAThread]
        private static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            try
            {
                LaunchOptions options = LaunchOptions.Parse(args);
                string appDirectory = AppDomain.CurrentDomain.BaseDirectory;
                string serverPath = Path.Combine(appDirectory, "server.py");
                string dataDirectory = options.DataDirectory ?? Path.Combine(appDirectory, "data");
                string appUrl = "http://127.0.0.1:" + options.Port + "/";
                string healthUrl = appUrl + "api/health";

                if (!File.Exists(serverPath))
                {
                    Fail("server.py was not found beside Home Capture.exe.\n\nExpected: " + serverPath);
                    return;
                }

                if (!IsHealthy(healthUrl))
                {
                    Process serverProcess;
                    string failure;
                    if (!TryStartBackend(appDirectory, serverPath, dataDirectory, options.Port, out serverProcess, out failure))
                    {
                        Fail(failure);
                        return;
                    }

                    bool becameHealthy = false;
                    for (int attempt = 0; attempt < 80; attempt++)
                    {
                        Thread.Sleep(250);
                        if (IsHealthy(healthUrl))
                        {
                            becameHealthy = true;
                            break;
                        }
                        if (serverProcess.HasExited)
                        {
                            break;
                        }
                    }

                    if (!becameHealthy)
                    {
                        string exitDetail = serverProcess.HasExited
                            ? "The backend exited with code " + serverProcess.ExitCode + "."
                            : "The backend did not become healthy within 20 seconds.";
                        Fail(
                            "Home Capture could not become operational.\n\n" + exitDetail +
                            "\n\nAnother application may be using port " + options.Port +
                            ", or Python may be unable to start the local server."
                        );
                        return;
                    }
                }

                if (!options.NoOpen)
                {
                    OpenAppWindow(appUrl);
                }
            }
            catch (Exception exception)
            {
                Fail("Home startup failed.\n\n" + exception.Message);
            }
        }

        private static bool IsHealthy(string healthUrl)
        {
            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(healthUrl);
                request.Method = "GET";
                request.Timeout = 1000;
                request.ReadWriteTimeout = 1000;
                request.Proxy = null;
                using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                using (StreamReader reader = new StreamReader(response.GetResponseStream()))
                {
                    if (response.StatusCode != HttpStatusCode.OK)
                    {
                        return false;
                    }
                    string body = reader.ReadToEnd();
                    return Regex.IsMatch(body, "\\\"service\\\"\\s*:\\s*\\\"" + ServiceName + "\\\"")
                        && Regex.IsMatch(body, "\\\"status\\\"\\s*:\\s*\\\"operational\\\"");
                }
            }
            catch
            {
                return false;
            }
        }

        private static bool TryStartBackend(
            string appDirectory,
            string serverPath,
            string dataDirectory,
            int port,
            out Process process,
            out string failure)
        {
            process = null;
            failure = null;

            PythonCommand python = FindPython();
            if (python == null)
            {
                failure = "Python 3 was not found. Install Python 3, then launch Home Capture again.";
                return false;
            }

            Directory.CreateDirectory(dataDirectory);
            string arguments = python.PrefixArguments
                + Quote(serverPath)
                + " --host 127.0.0.1"
                + " --port " + port
                + " --data-dir " + Quote(dataDirectory)
                + " --access-mode desktop";

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.FileName = python.Executable;
            startInfo.Arguments = arguments;
            startInfo.WorkingDirectory = appDirectory;
            startInfo.UseShellExecute = false;
            startInfo.CreateNoWindow = true;
            startInfo.WindowStyle = ProcessWindowStyle.Hidden;

            try
            {
                process = Process.Start(startInfo);
                if (process == null)
                {
                    failure = "Windows did not create the Home backend process.";
                    return false;
                }
                return true;
            }
            catch (Exception exception)
            {
                failure = "The Home backend could not start.\n\n" + exception.Message;
                return false;
            }
        }

        private static PythonCommand FindPython()
        {
            string[] names = { "pythonw.exe", "python.exe", "pyw.exe", "py.exe" };
            string pathValue = Environment.GetEnvironmentVariable("PATH") ?? string.Empty;
            string[] pathDirectories = pathValue.Split(Path.PathSeparator);

            foreach (string name in names)
            {
                foreach (string rawDirectory in pathDirectories)
                {
                    string directory = rawDirectory.Trim().Trim('"');
                    if (directory.Length == 0)
                    {
                        continue;
                    }
                    string candidate = Path.Combine(directory, name);
                    if (File.Exists(candidate))
                    {
                        bool isPythonLauncher = string.Equals(name, "py.exe", StringComparison.OrdinalIgnoreCase)
                            || string.Equals(name, "pyw.exe", StringComparison.OrdinalIgnoreCase);
                        return new PythonCommand(candidate, isPythonLauncher ? "-3 " : string.Empty);
                    }
                }

                string windowsCandidate = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), name);
                if (File.Exists(windowsCandidate))
                {
                    bool isPythonLauncher = string.Equals(name, "py.exe", StringComparison.OrdinalIgnoreCase)
                        || string.Equals(name, "pyw.exe", StringComparison.OrdinalIgnoreCase);
                    return new PythonCommand(windowsCandidate, isPythonLauncher ? "-3 " : string.Empty);
                }
            }
            return null;
        }

        private static void OpenAppWindow(string appUrl)
        {
            string programFiles = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);
            string programFilesX86 = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86);
            string localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string[] browserCandidates =
            {
                Path.Combine(programFilesX86, "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(programFiles, "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(localAppData, "Microsoft", "Edge", "Application", "msedge.exe"),
                Path.Combine(programFiles, "Google", "Chrome", "Application", "chrome.exe"),
                Path.Combine(programFilesX86, "Google", "Chrome", "Application", "chrome.exe")
            };

            foreach (string browser in browserCandidates)
            {
                if (!File.Exists(browser))
                {
                    continue;
                }
                ProcessStartInfo browserStart = new ProcessStartInfo();
                browserStart.FileName = browser;
                browserStart.Arguments = "--app=" + Quote(appUrl) + " --new-window";
                browserStart.UseShellExecute = false;
                browserStart.CreateNoWindow = true;
                Process.Start(browserStart);
                return;
            }

            ProcessStartInfo fallback = new ProcessStartInfo();
            fallback.FileName = appUrl;
            fallback.UseShellExecute = true;
            Process.Start(fallback);
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }

        private static void Fail(string message)
        {
            MessageBox.Show(
                message,
                "Home Capture could not start",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );
        }

        private sealed class PythonCommand
        {
            internal PythonCommand(string executable, string prefixArguments)
            {
                Executable = executable;
                PrefixArguments = prefixArguments;
            }

            internal string Executable { get; private set; }
            internal string PrefixArguments { get; private set; }
        }

        private sealed class LaunchOptions
        {
            internal bool NoOpen { get; private set; }
            internal int Port { get; private set; }
            internal string DataDirectory { get; private set; }

            private LaunchOptions()
            {
                Port = 8765;
            }

            internal static LaunchOptions Parse(string[] args)
            {
                LaunchOptions options = new LaunchOptions();
                for (int index = 0; index < args.Length; index++)
                {
                    string argument = args[index];
                    if (string.Equals(argument, "--no-open", StringComparison.OrdinalIgnoreCase))
                    {
                        options.NoOpen = true;
                    }
                    else if (string.Equals(argument, "--port", StringComparison.OrdinalIgnoreCase) && index + 1 < args.Length)
                    {
                        int port;
                        if (!int.TryParse(args[++index], out port) || port < 1 || port > 65535)
                        {
                            throw new ArgumentException("--port must be an integer from 1 through 65535.");
                        }
                        options.Port = port;
                    }
                    else if (string.Equals(argument, "--data-dir", StringComparison.OrdinalIgnoreCase) && index + 1 < args.Length)
                    {
                        options.DataDirectory = Path.GetFullPath(args[++index]);
                    }
                    else
                    {
                        throw new ArgumentException("Unknown launcher argument: " + argument);
                    }
                }
                return options;
            }
        }
    }
}
