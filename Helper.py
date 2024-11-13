from pytubefix import Search


class Helper:
    @staticmethod
    def get_results_by(request):
        if request.startswith("https://"):
            s = Search(request).videos
            return s[0]
        else:
            s = Search(request).videos
            return s
