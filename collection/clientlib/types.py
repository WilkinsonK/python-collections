from requests import Session, Response

NotSet            = type("NotSet", (int,), {})
ConnectionTimeout = type("ConnectionTimeout", (float,), {})
ReadTimeout       = type("ReadTimeout", (float,), {})
