from stackifyapm.protos import stackify_trace_pb2


def _spans_to_protobuf(frames, spans):
    for span in spans:
        frame = stackify_trace_pb2.TraceFrame()
        frame.call = span['call']
        frame.start_timestamp_millis = span['reqBegin']
        frame.end_timestamp_millis = span['reqEnd']
        frame.properties.update(span['props'])
        _spans_to_protobuf(frame.frames, span.get('stacks', []))
        frames.append(frame)

    return frames


def to_protobuf(transaction):
    trace = stackify_trace_pb2.Trace()
    trace.frame.call = transaction['call']
    trace.frame.start_timestamp_millis = transaction['reqBegin']
    trace.frame.end_timestamp_millis = transaction['reqEnd']
    trace.frame.properties.update(transaction['props'])
    _spans_to_protobuf(trace.frame.frames, transaction['stacks'])

    if transaction.get('exceptions'):
        for exception in transaction['exceptions']:
            trace_exception = stackify_trace_pb2.TraceException()
            trace_exception.caught_by = exception['CaughtBy']
            trace_exception.exception = exception['Exception']
            trace_exception.message = exception['Message']
            trace_exception.timestamp_millis = int(exception['Timestamp'])

            for frame in exception['Frames']:
                trace_exception_frame = stackify_trace_pb2.TraceExceptionFrame()
                trace_exception_frame.method = frame['Method']
                trace_exception.frames.append(trace_exception_frame)

            trace.frame.exceptions.append(trace_exception)

    return trace
