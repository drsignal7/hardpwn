import datetime

class GlitchLab:
    def __init__(self, transport, db=None):
        """
        transport: object implementing glitch_voltage(pulse_ns, delay_ns),
                   glitch_clock(...), glitch_reset(...)
        """
        self.t = transport
        self.db = db

    def run_campaigns(self, campaigns=None):
        if campaigns is None:
            campaigns = [{'kind':'voltage','pulse_widths':[50,100,200],'delays':[0,50,100],'repeats':3}]
        results = []
        for c in campaigns:
            kind = c.get('kind','voltage')
            for pw in c.get('pulse_widths', [50]):
                for d in c.get('delays',[0]):
                    for r in range(0, c.get('repeats',1)):
                        res = self._single_attempt(kind, pw, d)
                        entry = {'when': datetime.datetime.now().isoformat(), 'kind':kind, 'pw_ns':pw, 'delay_ns':d, 'iter':r, 'result':res}
                        results.append(entry)
                        if self.db:
                            self.db.log_glitch({'kind':kind,'pw_ns':pw,'delay_ns':d,'iter':r}, res)
        return results

    def _single_attempt(self, kind, pw, delay):
        try:
            if kind == 'voltage':
                return self.t.glitch_voltage(pw, delay)
            elif kind == 'clock':
                return self.t.glitch_clock(pw, delay)
            elif kind == 'reset':
                return self.t.glitch_reset(pw, delay)
            else:
                return {'status':'unknown_kind'}
        except Exception as e:
            return {'status':'error','error':str(e)}
