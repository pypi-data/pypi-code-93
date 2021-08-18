
import os
import multiprocessing
from pynori.korean_analyzer import KoreanAnalyzer
from pynori.utils import set_logger

logger = set_logger()


def worker_function(read_path, write_path, worker_id, kwargs, start_offset=0, end_offset=-1):
	""" 단일 프로세스에 사용되는 worker 함수 """
	logger.info(f"[Start] worker_id: {worker_id} [start_offset: {start_offset} & end_offset: {end_offset}]")
	nori = KoreanAnalyzer(**kwargs)
	rf = open(read_path, 'r', encoding="utf-8")
	with open(f"{write_path}_{worker_id}", 'w', encoding="utf-8") as wf:
		cnt = 0
		for line in rf:
			cnt += 1
			line = line.strip()
			if cnt <= start_offset or cnt > end_offset:
				continue
			if line is None or len(line) == 0:
				continue
			token_list = nori.do_analysis(line)['termAtt'] # only termAtt
			tokenized_line = " ".join(token_list)
			wf.write(tokenized_line + '\n')
	rf.close()


class KoreanAnalyzerMultiprocessing:
	""" KoreanAnalyzer 를 multiprocessing 으로 수행하기 위한 클래스.
	KoreanAnalyzer 와 동일하게 옵션으로 클래스를 초기화.
	"""
	def __init__(self, **kwargs):
		self.kwargs = kwargs

	def run(self, num_workers=3, read_path=None, write_path=None):
		if read_path is None or not os.path.exists(read_path):
			logger.error(f"\n\t[Error] Please check your read file path - \"{read_path}\"\n")
			exit()
		offsets = get_offset_ranges(read_path, num_workers)
		logger.info(f"file offsets based on number of workers: {offsets}")

		pool = multiprocessing.Pool(processes=num_workers)
		logger.info(f"[Start] Multiprocessing. number of workers: {num_workers}")
		for worker_id in range(num_workers):
			pool.apply_async(
				worker_function,
				(read_path, write_path, worker_id, self.kwargs, offsets[worker_id], offsets[worker_id+1])
			)
		pool.close()
		logger.info("[Complete] join all workers")
		pool.join()

		merge_worker_files(num_workers, write_path)
		logger.info("[Complete] merge all worker files to path: \"{write_path}\"")
		for worker_id in range(num_workers):
			if os.path.exists(f"{write_path}_{worker_id}"):
				os.remove(f"{write_path}_{worker_id}")
		logger.info(f"[End] Multiprocessing.")

def _get_file_counts(path):
	with open(path, 'r', encoding="utf-8") as rf:
		for i, _ in enumerate(rf):
			pass
	return i + 1

def get_offset_ranges(read_path, num_workers):
	count = _get_file_counts(read_path)
	assert count > num_workers
	step_sz = int(count / num_workers)
	offset_ranges = [0]
	pv_cnt = 1
	for i in range(num_workers):
		if i == num_workers-1:
			pv_cnt = count
		else:
			pv_cnt = pv_cnt + step_sz
		offset_ranges.append(pv_cnt)
	return offset_ranges
				
def merge_worker_files(num_workers, write_path):
	total_cnt = 0
	worker_files = [f"{write_path}_{x}" for x in range(num_workers)]
	wf = open(write_path, 'w', encoding='utf-8')
	for file in worker_files:
		with open(file, 'r', encoding='utf-8') as rf:
			for line in rf:
				line = line.strip()
				wf.write(line + '\n')
				total_cnt += 1
	logger.info(f"[Complete] merge worker files. total cnt: {total_cnt}")
	wf.close()


if __name__ == "__main__":

	nori_mp = KoreanAnalyzerMultiprocessing(
		decompound_mode='MIXED',
		infl_decompound_mode='MIXED',
	)

	nori_mp.run(num_workers=3, 
				read_path="", 
				write_path="")