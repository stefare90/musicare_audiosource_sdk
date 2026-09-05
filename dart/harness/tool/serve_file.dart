import 'dart:io';

void main(List<String> args) async {
  if (args.isEmpty) {
    stderr.writeln(
      'Usage: dart run tool/serve_file.dart <path_to_file> [port]',
    );
    exit(1);
  }

  final targetFile = File(args[0]);
  if (!targetFile.existsSync()) {
    stderr.writeln('Error: File not found at: ${targetFile.path}');
    exit(1);
  }

  final port = args.length > 1 ? int.parse(args[1]) : 8888;
  final server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);

  stdout.writeln('SERVER_RUNNING on http://127.0.0.1:$port');

  await for (final HttpRequest request in server) {
    // Serve the target file for any GET request matching the filename or root
    request.response.headers.contentType = ContentType('application', 'zip');
    request.response.headers.add('Access-Control-Allow-Origin', '*');

    await request.response.addStream(targetFile.openRead());
    await request.response.close();
  }
}
